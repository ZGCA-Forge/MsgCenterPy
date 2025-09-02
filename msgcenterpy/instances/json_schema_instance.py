from typing import TYPE_CHECKING, Any, Dict, Optional

import jsonschema

from msgcenterpy.core.envelope import MessageEnvelope, create_envelope
from msgcenterpy.core.message_instance import MessageInstance
from msgcenterpy.core.type_converter import TypeConverter
from msgcenterpy.core.type_info import ConstraintType, Consts, TypeInfo
from msgcenterpy.core.types import MessageType

if TYPE_CHECKING:
    from msgcenterpy.core.field_accessor import FieldAccessor


class JSONSchemaMessageInstance(MessageInstance[Dict[str, Any]]):
    """JSON Schema消息实例，支持类型信息提取和字段访问器"""

    _validation_errors: list[str] = []
    _json_schema: Dict[str, Any] = dict()
    _json_data: Dict[str, Any] = dict()

    def __init__(self, inner_data: Dict[str, Any], schema: Dict[str, Any], **kwargs: Any) -> None:
        """
        初始化JSON Schema消息实例

        Args:
            inner_data: JSON数据字典
            schema: JSON Schema定义（必需）
        """
        # 直接存储schema和data
        self._json_schema = schema
        self._json_data = inner_data
        self._validation_errors = []
        # 验证数据
        self._validate_data()
        super().__init__(inner_data, MessageType.JSON_SCHEMA)

    @property
    def json_schema(self) -> Dict[str, Any]:
        """获取JSON Schema"""
        return self._json_schema

    def _validate_data(self) -> None:
        """根据schema验证数据"""
        try:
            jsonschema.validate(self._json_data, self._json_schema)
        except jsonschema.ValidationError as e:
            # 不抛出异常，只记录验证错误
            self._validation_errors = [str(e)]
        except Exception:
            self._validation_errors = ["Schema validation failed"]
        else:
            self._validation_errors = []

    def export_to_envelope(self, **kwargs: Any) -> MessageEnvelope:
        """导出为统一信封字典"""
        base_dict = self.get_python_dict()

        envelope = create_envelope(
            format_name=self.message_type.value,
            content=base_dict,
            metadata={
                "current_format": self.message_type.value,
                "source_cls_name": self.__class__.__name__,
                "source_cls_module": self.__class__.__module__,
                **self._metadata,
            },
        )
        return envelope

    @classmethod
    def import_from_envelope(cls, data: MessageEnvelope, **kwargs: Any) -> "JSONSchemaMessageInstance":
        """从规范信封创建JSON Schema实例"""
        content = data["content"]
        properties = data["metadata"]["properties"]
        json_schema = properties["json_schema"]
        instance = cls(content, json_schema)
        return instance

    def get_python_dict(self) -> Dict[str, Any]:
        """获取当前所有的字段名和对应的原始值"""
        return self._json_data.copy()

    def set_python_dict(self, value: Dict[str, Any], **kwargs: Any) -> bool:
        """设置所有字段的值，只做已有字段的更新"""
        # 获取根访问器
        root_accessor = self._field_accessor
        if root_accessor is not None:
            root_accessor.update_from_dict(source_data=value)
        # 重新验证数据
        self._validate_data()
        return True

    def _get_schema_from_path(self, path: str) -> Dict[str, Any]:
        """根据访问器路径获取对应的JSON Schema定义

        Args:
            path: 字段访问器的完整路径，如 "MSG_CENTER_ROOT.user.address"

        Returns:
            对应路径的JSON Schema定义
        """
        # 移除根路径前缀
        if path.startswith(Consts.ACCESSOR_ROOT_NODE):
            if path == Consts.ACCESSOR_ROOT_NODE:
                return self._json_schema
            path = path[len(Consts.ACCESSOR_ROOT_NODE) + 1 :]

        # 如果路径为空，返回根schema
        if not path:
            return self._json_schema

        # 分割路径并逐级导航
        path_parts = path.split(".")
        current_schema = self._json_schema

        for part in path_parts:
            # 检查当前schema是否有properties
            if "properties" not in current_schema:
                return {}

            properties = current_schema["properties"]
            if part not in properties:
                return {}

            current_schema = properties[part]

            # 如果当前schema是数组，需要获取items的schema
            if current_schema.get("type") == "array" and "items" in current_schema:
                current_schema = current_schema["items"]

        return current_schema

    def _get_property_schema_for_field(self, field_name: str, parent_field_accessor: "FieldAccessor") -> Dict[str, Any]:
        """获取字段的JSON Schema属性定义

        Args:
            field_name: 字段名
            parent_field_accessor: 父级字段访问器

        Returns:
            字段的JSON Schema属性定义
        """
        # 获取父级的schema定义
        parent_schema = self._get_schema_from_path(parent_field_accessor.full_path_from_root)

        # 从父级schema的properties中获取字段定义
        if "properties" in parent_schema:
            return parent_schema["properties"].get(field_name, {})  # type: ignore[no-any-return]
        elif parent_schema.get("type") == "array" and "items" in parent_schema:
            # 如果父级是数组，获取items的属性
            items_schema = parent_schema["items"]
            if "properties" in items_schema:
                return items_schema["properties"].get(field_name, {})  # type: ignore[no-any-return]

        return {}

    # TypeInfoProvider 接口实现
    def get_field_type_info(
        self, field_name: str, field_value: Any, parent_field_accessor: "FieldAccessor"
    ) -> Optional[TypeInfo]:
        """从JSON Schema定义中提取字段类型信息"""
        # 构建完整路径
        full_path = f"{parent_field_accessor.full_path_from_root}.{field_name}"

        # 获取字段的JSON Schema定义
        property_schema = self._get_property_schema_for_field(field_name, parent_field_accessor)

        # 确定类型信息
        python_type = type(field_value)
        if "type" in property_schema:
            json_type = property_schema["type"]
            standard_type = TypeConverter.json_schema_type_to_standard(json_type)
        else:
            # 如果schema中没有类型定义，从Python类型推断
            standard_type = TypeConverter.python_type_to_standard(python_type)
            json_type = TypeConverter.standard_type_to_json_schema_type(standard_type)

        # 创建基础TypeInfo
        type_info = TypeInfo(
            field_name=field_name,
            field_path=full_path,
            standard_type=standard_type,
            python_type=python_type,
            original_type=json_type,
            current_value=field_value,
        )

        # 提取约束信息
        self._extract_constraints_from_schema(type_info, property_schema)

        # 检查字段是否在父级的required列表中
        parent_schema = self._get_schema_from_path(parent_field_accessor.full_path_from_root)
        required_fields = parent_schema.get("required", [])
        if field_name in required_fields:
            type_info.add_constraint(ConstraintType.REQUIRED, True, "Field is required by JSON Schema")

        # 处理数组类型
        if json_type == "array":
            type_info.is_array = True
            self._extract_array_constraints(type_info, property_schema)

        # 处理对象类型
        elif json_type == "object":
            type_info.is_object = True
            self._extract_object_constraints(type_info, property_schema)

        # 设置默认值
        if "default" in property_schema:
            type_info.default_value = property_schema["default"]

        return type_info

    @classmethod
    def _extract_constraints_from_schema(cls, type_info: TypeInfo, property_schema: Dict[str, Any]) -> None:
        """从JSON Schema属性中提取约束条件"""
        # 数值约束
        if "minimum" in property_schema:
            type_info.add_constraint(ConstraintType.MIN_VALUE, property_schema["minimum"])
        if "maximum" in property_schema:
            type_info.add_constraint(ConstraintType.MAX_VALUE, property_schema["maximum"])
        if "exclusiveMinimum" in property_schema:
            type_info.add_constraint(ConstraintType.EXCLUSIVE_MIN, property_schema["exclusiveMinimum"])
        if "exclusiveMaximum" in property_schema:
            type_info.add_constraint(ConstraintType.EXCLUSIVE_MAX, property_schema["exclusiveMaximum"])
        if "multipleOf" in property_schema:
            type_info.add_constraint(ConstraintType.MULTIPLE_OF, property_schema["multipleOf"])

        # 字符串约束
        if "minLength" in property_schema:
            type_info.add_constraint(ConstraintType.MIN_LENGTH, property_schema["minLength"])
        if "maxLength" in property_schema:
            type_info.add_constraint(ConstraintType.MAX_LENGTH, property_schema["maxLength"])
        if "pattern" in property_schema:
            type_info.add_constraint(ConstraintType.PATTERN, property_schema["pattern"])

        # 枚举约束
        if "enum" in property_schema:
            type_info.add_constraint(ConstraintType.ENUM_VALUES, property_schema["enum"])

        # 格式约束
        if "format" in property_schema:
            type_info.add_constraint(ConstraintType.FORMAT, property_schema["format"])

        # 默认值
        if "default" in property_schema:
            type_info.add_constraint(ConstraintType.DEFAULT_VALUE, property_schema["default"])

    @classmethod
    def _extract_array_constraints(cls, type_info: TypeInfo, property_schema: Dict[str, Any]) -> None:
        """提取数组类型的约束"""
        if "minItems" in property_schema:
            type_info.add_constraint(ConstraintType.MIN_ITEMS, property_schema["minItems"])
        if "maxItems" in property_schema:
            type_info.add_constraint(ConstraintType.MAX_ITEMS, property_schema["maxItems"])
        if "uniqueItems" in property_schema:
            type_info.add_constraint(ConstraintType.UNIQUE_ITEMS, property_schema["uniqueItems"])

        # 提取数组元素类型信息
        items_schema = property_schema.get("items")
        if isinstance(items_schema, dict) and "type" in items_schema:
            element_type = TypeConverter.json_schema_type_to_standard(items_schema["type"])
            type_info.element_type_info = TypeInfo(
                field_name=f"{type_info.field_name}_item",
                field_path=f"{type_info.field_path}_item",
                standard_type=element_type,
                python_type=TypeConverter.standard_to_python_type(element_type),
                original_type=items_schema["type"],
                current_value=None,
            )
            # 递归提取元素约束
            cls._extract_constraints_from_schema(type_info.element_type_info, items_schema)

    @classmethod
    def _extract_object_constraints(cls, type_info: TypeInfo, property_schema: Dict[str, Any]) -> None:
        """提取对象类型的约束"""
        # 对象类型的属性定义
        properties = property_schema.get("properties", {})
        required_fields = property_schema.get("required", [])

        for prop_name, prop_schema in properties.items():
            if isinstance(prop_schema, dict) and "type" in prop_schema:
                prop_type = TypeConverter.json_schema_type_to_standard(prop_schema["type"])
                prop_type_info = TypeInfo(
                    field_name=prop_name,
                    field_path=f"{type_info.field_path}.{prop_name}",
                    standard_type=prop_type,
                    python_type=TypeConverter.standard_to_python_type(prop_type),
                    original_type=prop_schema["type"],
                    current_value=None,
                )
                # 递归提取属性约束
                cls._extract_constraints_from_schema(prop_type_info, prop_schema)

                # 如果字段在required列表中，添加REQUIRED约束
                if prop_name in required_fields:
                    prop_type_info.add_constraint(
                        ConstraintType.REQUIRED,
                        True,
                        "Field is required by JSON Schema",
                    )

                type_info.object_fields[prop_name] = prop_type_info
