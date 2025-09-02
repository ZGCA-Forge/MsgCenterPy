from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, cast

from msgcenterpy.core.type_converter import StandardType
from msgcenterpy.core.type_info import (
    ConstraintType,
    Consts,
    TypeInfo,
    TypeInfoPostProcessor,
)
from msgcenterpy.utils.decorator import experimental

TEST_MODE = True


class FieldAccessor:
    """
    字段访问器，支持类型转换和约束验证的统一字段访问接口
    只需要getitem和setitem，外部必须通过字典的方式来赋值
    """

    @property
    def parent_msg_center(self) -> Optional["FieldAccessor"]:
        return self._parent

    @property
    def full_path_from_root(self) -> str:
        if self._parent is None:
            return self._field_name or "unknown"
        else:
            parent_path = self._parent.full_path_from_root
            return f"{parent_path}.{self._field_name or 'unknown'}"

    @property
    def root_accessor_msg_center(self) -> "FieldAccessor":
        """获取根访问器"""
        current = self
        while current._parent is not None:
            current = current._parent
        return current

    @property
    def value(self) -> Any:
        return self._data

    @value.setter
    def value(self, data: Any) -> None:
        if self._parent is not None and self._field_name is not None:
            self._parent[self._field_name] = data

    @property
    def type_info(self) -> Optional[TypeInfo]:
        if self._type_info is not None:
            return self._type_info

        # 如果是根accessor或者没有字段名，无法获取TypeInfo
        if self._parent is None or self._field_name is None:
            return None

        # 调用类型信息提供者获取类型信息，调用是耗时的
        if self._type_info_provider is None:
            return None
        type_info = self._type_info_provider.get_field_type_info(self._field_name, self._data, self._parent)

        # 对TypeInfo进行后处理，添加默认约束
        if type_info:
            TypeInfoPostProcessor.post_process_type_info(type_info)
            self._type_info = type_info

        return type_info

    """标记方便排除getitem/setitem，不要删除"""
    _data: Any = None
    _type_info_provider: "TypeInfoProvider" = None  # type: ignore[assignment]
    _parent: Optional["FieldAccessor"] = None
    _field_name: str = None  # type: ignore[assignment]
    _cache: Dict[str, "FieldAccessor"] = None  # type: ignore[assignment]
    _type_info: Optional[TypeInfo] = None

    def __init__(
        self,
        data: Any,
        type_info_provider: "TypeInfoProvider",
        parent: Optional["FieldAccessor"],
        field_name: str,
    ):
        """
        初始化字段访问器

        Args:
            data: 要访问的数据对象
            type_info_provider: 类型信息提供者
            parent: 父字段访问器，用于嵌套访问
            field_name: 当前访问器对应的字段名（用于构建路径）
        """
        self._data = data
        self._type_info_provider = type_info_provider
        self._parent = parent
        self._field_name = field_name
        self._cache: Dict[str, "FieldAccessor"] = {}  # 缓存FieldAccessor而不是TypeInfo
        self._type_info: Optional[TypeInfo] = None  # 当前accessor的TypeInfo

    def get_sub_type_info(self, field_name: str) -> Optional[TypeInfo]:
        """获取字段的类型信息，通过获取字段的accessor"""
        field_accessor = self[field_name]
        return field_accessor.type_info

    def __getitem__(self, field_name: str) -> "FieldAccessor":
        """获取字段访问器，支持嵌套访问"""
        # 检查缓存中是否有对应的 accessor
        if self._cache is None:
            self._cache = {}
        if field_name in self._cache:
            cached_accessor = self._cache[field_name]
            # 更新 accessor 的数据源，以防数据已更改
            if TEST_MODE:
                raw_value = self._get_raw_value(field_name)
                if cached_accessor.value != raw_value:
                    raise ValueError(
                        f"Cached accessor value mismatch for field '{field_name}': expected {raw_value}, got {cached_accessor.value}"
                    )
            return cached_accessor
        # 获取原始值并创建新的 accessor
        raw_value = self._get_raw_value(field_name)
        if self._type_info_provider is None:
            raise RuntimeError("TypeInfoProvider not initialized")
        accessor = FieldAccessorFactory.create_accessor(
            data=raw_value,
            type_info_provider=self._type_info_provider,
            parent=self,
            field_name=field_name,
        )

        self._cache[field_name] = accessor
        return accessor

    def __setitem__(self, field_name: str, value: Any) -> None:
        """设置字段值，支持类型转换和验证"""
        # 获取类型信息
        if field_name in self._get_field_names():
            type_info = self.get_sub_type_info(field_name)
            if type_info is not None:
                # 进行类型转换
                converted_value = type_info.convert_value(value)  # 这步自带validate
                value = converted_value
            # 对子field设置value，依然会上溯走set_raw_value，确保一致性
        # 设置值
        sub_accessor = self[field_name]
        self._set_raw_value(field_name, value)
        sub_accessor._data = self._get_raw_value(field_name)  # 有可能内部还有赋值的处理
        # 清除相关缓存
        self.clear_cache(field_name)

    def __contains__(self, field_name: str) -> bool:
        return self._has_field(field_name)

    def __getattr__(self, field_name: str) -> "FieldAccessor | Any":
        """支持通过属性访问字段，用于嵌套访问如 accessor.pose.position.x"""
        for cls in self.__class__.__mro__:
            if field_name in cls.__dict__:
                return cast(Any, super().__getattribute__(field_name))
        return self[field_name]

    def __setattr__(self, field_name: str, value: Any) -> None:
        """支持通过属性设置字段值，用于嵌套赋值如 accessor.pose.position.x = 1.0"""
        for cls in self.__class__.__mro__:
            if field_name in cls.__dict__:
                return super().__setattr__(field_name, value)
        self[field_name] = value
        return None

    def clear_cache(self, field_name: Optional[str] = None) -> None:
        """失效字段相关的缓存"""
        if self._cache is not None and field_name is not None and field_name in self._cache:
            self._cache[field_name].clear_type_info()

    def clear_type_info(self) -> None:
        """清空所有缓存"""
        if self._type_info is not None:
            self._type_info._outdated = True
        self._type_info = None

    def get_nested_field_accessor(self, path: str, separator: str = ".") -> "FieldAccessor":
        parts = path.split(separator)
        current = self
        for part in parts:
            current = self[part]
        return current

    def set_nested_value(self, path: str, value: Any, separator: str = ".") -> None:
        current = self.get_nested_field_accessor(path, separator)
        current.value = value

    def _get_raw_value(self, field_name: str) -> Any:
        """获取原始字段值（子类实现）"""
        if hasattr(self._data, "__getitem__"):
            return self._data[field_name]
        elif hasattr(self._data, field_name):
            return getattr(self._data, field_name)
        else:
            raise KeyError(f"Field {field_name} not found")

    def _set_raw_value(self, field_name: str, value: Any) -> None:
        """设置原始字段值（子类实现）"""
        if hasattr(self._data, "__setitem__"):
            self._data[field_name] = value
        elif hasattr(self._data, field_name):
            setattr(self._data, field_name, value)
        else:
            raise KeyError(f"Field {field_name} not found")

    def _has_field(self, field_name: str) -> bool:
        """检查字段是否存在（子类实现）"""
        if hasattr(self._data, "__contains__"):
            return field_name in self._data
        else:
            return field_name in self._get_field_names()

    def _get_field_names(self) -> list[str]:
        """获取所有字段名（子类实现）"""
        if callable(getattr(self._data, "keys", None)):
            # noinspection PyCallingNonCallable
            return list(self._data.keys())
        elif hasattr(self._data, "__dict__"):
            return list(self._data.__dict__.keys())
        elif hasattr(self._data, "__slots__"):
            # noinspection PyTypeChecker
            return list(self._data.__slots__)
        else:
            # 回退方案：使用dir()但过滤掉特殊方法
            return [name for name in dir(self._data) if not name.startswith("_")]

    def get_json_schema(self) -> Dict[str, Any]:
        """原有的递归生成 JSON Schema 逻辑"""
        # 获取当前访问器的类型信息
        current_type_info = self.type_info

        # 如果当前层级有类型信息，使用它生成基本schema
        if current_type_info is not None:
            schema = current_type_info.to_json_schema_property()
        else:
            # 如果没有类型信息，创建基本的object schema
            schema = {"type": "object", "additionalProperties": True}

        # 如果这是一个对象类型，需要递归处理其字段
        if schema.get("type") == "object":
            properties = {}
            required_fields = []

            # 获取所有字段名
            field_names = self._get_field_names()

            for field_name in field_names:
                try:
                    # 获取字段的访问器
                    field_accessor = self[field_name]
                    field_type_info = field_accessor.type_info

                    if field_type_info is not None:
                        # 根据字段类型决定如何生成schema
                        if field_type_info.standard_type == StandardType.OBJECT:
                            # 对于嵌套对象，递归调用
                            field_schema = field_accessor.get_json_schema()
                        else:
                            # 对于基本类型，直接使用type_info转换
                            field_schema = field_type_info.to_json_schema_property()

                        properties[field_name] = field_schema

                        # 检查是否为必需字段
                        if field_type_info.has_constraint(ConstraintType.REQUIRED):
                            required_fields.append(field_name)

                except Exception as e:
                    # 如果字段处理失败，记录警告但继续处理其他字段
                    print(f"Warning: Failed to generate schema for field '{field_name}': {e}")
                    continue

            # 更新schema中的properties
            if properties:
                schema["properties"] = properties

            # 设置必需字段
            if required_fields:
                schema["required"] = required_fields

            # 如果没有字段信息，允许额外属性
            if not properties:
                schema["additionalProperties"] = True
            else:
                schema["additionalProperties"] = False

        return schema

    @experimental("Feature under development")
    def update_from_dict(self, source_data: Dict[str, Any]) -> None:
        """递归更新嵌套字典

        Args:
            source_data: 源数据字典
        """
        for key, new_value in source_data.items():
            field_exists = self._has_field(key)
            could_add = self._could_allow_new_field(key, new_value)
            if field_exists:
                current_field_accessor = self[key]
                current_type_info = current_field_accessor.type_info
                # 当前key: Object，交给子dict去迭代
                if (
                    current_type_info
                    and current_type_info.standard_type == StandardType.OBJECT
                    and isinstance(new_value, dict)
                ):
                    current_field_accessor.update_from_dict(new_value)
                # 当前key: Array，每个值要交给子array去迭代
                elif (
                    current_type_info
                    and hasattr(current_type_info.standard_type, "IS_ARRAY")
                    and current_type_info.standard_type.IS_ARRAY
                    and isinstance(new_value, list)
                ):
                    # 存在情况Array嵌套，这里后续支持逐个赋值，可能需要利用iter进行赋值
                    self[key] = new_value
                else:
                    # 不限制类型 或 python类型包含
                    if could_add or (current_type_info and issubclass(type(new_value), current_type_info.python_type)):
                        self[key] = new_value
                    else:
                        raise ValueError(f"{key}")
            elif could_add:
                self[key] = new_value

    def _could_allow_new_field(self, field_name: str, field_value: Any) -> bool:
        """检查是否应该允许添加新字段

        通过检查当前type_info中的TYPE_KEEP约束来判断：
        - 如果有TYPE_KEEP且为True，说明类型结构固定，不允许添加新字段
        - 如果没有TYPE_KEEP约束或为False，则允许添加新字段

        Args:
            field_name: 字段名
            field_value: 字段值

        Returns:
            是否允许添加该字段
        """
        parent_type_info = self.type_info
        if parent_type_info is None:
            return True  # DEBUGGER NEEDED
        type_keep_constraint = parent_type_info.get_constraint(ConstraintType.TYPE_KEEP)
        if type_keep_constraint is not None and type_keep_constraint.value:
            return False
        return True


class TypeInfoProvider(ABC):
    """Require All Message Instances Extends This get_field_typ_info"""

    @abstractmethod
    def get_field_type_info(
        self, field_name: str, field_value: Any, field_accessor: "FieldAccessor"
    ) -> Optional[TypeInfo]:
        """获取指定字段的类型信息

        Args:
            field_name: 字段名，简单字段名如 'field'
            field_value: 字段的当前值，用于动态类型推断，不能为None
            field_accessor: 字段访问器，提供额外的上下文信息，不能为None

        Returns:
            字段的TypeInfo，如果字段不存在则返回None
        """
        pass


class ROS2FieldAccessor(FieldAccessor):
    def _get_raw_value(self, field_name: str) -> Any:
        return getattr(self._data, field_name)

    def _set_raw_value(self, field_name: str, value: Any) -> None:
        return setattr(self._data, field_name, value)

    def _has_field(self, field_name: str) -> bool:
        return hasattr(self._data, field_name)

    def _get_field_names(self) -> list[str]:
        if hasattr(self._data, "_fields_and_field_types"):
            # noinspection PyProtectedMember
            fields_and_types: Dict[str, str] = cast(Dict[str, str], self._data._fields_and_field_types)
            return list(fields_and_types.keys())
        else:
            return []


class FieldAccessorFactory:
    @staticmethod
    def create_accessor(
        data: Any,
        type_info_provider: TypeInfoProvider,
        parent: Optional[FieldAccessor] = None,
        field_name: str = Consts.ACCESSOR_ROOT_NODE,
    ) -> FieldAccessor:
        if hasattr(data, "_fields_and_field_types"):
            return ROS2FieldAccessor(data, type_info_provider, parent, field_name)
        else:
            return FieldAccessor(data, type_info_provider, parent, field_name)
