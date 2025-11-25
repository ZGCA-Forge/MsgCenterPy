"""
TypedDict Message Instance - Experimental

This module provides support for TypedDict message instances with type information
extraction and field access capabilities.

WARNING: This implementation is EXPERIMENTAL and may change in future versions.
"""

import warnings
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, get_type_hints

from msgcenterpy.core.envelope import MessageEnvelope, create_envelope
from msgcenterpy.core.message_instance import MessageInstance
from msgcenterpy.core.type_converter import TypeConverter
from msgcenterpy.core.type_info import ConstraintType, Consts, TypeInfo
from msgcenterpy.core.types import MessageType

if TYPE_CHECKING:
    from msgcenterpy.core.field_accessor import FieldAccessor


class TypedDictMessageInstance(MessageInstance[Dict[str, Any]]):
    """TypedDict消息实例，支持类型信息提取和字段访问器（实验性）

    EXPERIMENTAL: This class is experimental and may change in future versions.

    Attributes:
        _typed_dict_class: TypedDict类型定义
        _typed_dict_data: 实际的字典数据
        _pydantic_model: 缓存的Pydantic模型（懒加载）
        _json_schema: 缓存的JSON Schema（懒加载）
    """

    _typed_dict_class: Type[Any]
    _typed_dict_data: Dict[str, Any]
    _pydantic_model: Optional[Any] = None
    _json_schema: Optional[Dict[str, Any]] = None

    def __init__(self, inner_data: Dict[str, Any], typed_dict: Type[Any], **kwargs: Any) -> None:
        """
        初始化TypedDict消息实例

        Args:
            inner_data: 字典数据
            typed_dict: TypedDict类型定义
            **kwargs: 额外的关键字参数
        """
        # 发出实验性警告
        warnings.warn(
            "TypedDictMessageInstance is experimental and may change in future versions",
            FutureWarning,
            stacklevel=2,
        )

        # 验证typed_dict是否为TypedDict类型
        if not self._is_typed_dict(typed_dict):
            raise TypeError(f"Expected a TypedDict class, got {type(typed_dict)}")

        self._typed_dict_class = typed_dict
        self._typed_dict_data = inner_data
        self._pydantic_model = None
        self._json_schema = None

        super().__init__(inner_data, MessageType.TYPED_DICT)

    @staticmethod
    def _is_typed_dict(typed_dict_class: Type[Any]) -> bool:
        """检查给定的类是否为TypedDict"""
        try:
            # TypedDict类会有__annotations__和__total__等特殊属性
            return (
                hasattr(typed_dict_class, "__annotations__")
                and hasattr(typed_dict_class, "__total__")
                and hasattr(typed_dict_class, "__required_keys__")
                and hasattr(typed_dict_class, "__optional_keys__")
            )
        except Exception:
            return False

    @property
    def typed_dict_class(self) -> Type[Any]:
        """获取TypedDict类型定义"""
        return self._typed_dict_class

    @property
    def typed_dict_class_module(self) -> str:
        """获取TypedDict类的模块路径"""
        return self._typed_dict_class.__module__

    @property
    def typed_dict_class_name(self) -> str:
        """获取TypedDict类名"""
        return self._typed_dict_class.__name__

    @classmethod
    def get_pydantic_model_from_typed_dict(cls, typed_dict: Type[Any]) -> Any:
        """从TypedDict类型创建Pydantic模型（类方法版本）

        优先使用TypeAdapter（Pydantic V2），如果不可用则使用create_model_from_typeddict（Pydantic V1）

        Args:
            typed_dict: TypedDict类型定义

        Returns:
            Pydantic模型实例

        Raises:
            ImportError: 如果Pydantic未安装
            RuntimeError: 如果无法创建Pydantic模型
        """
        # 尝试使用Pydantic V2的TypeAdapter
        try:
            from pydantic import TypeAdapter

            adapter = TypeAdapter(typed_dict)
            return adapter
        except ImportError:
            pass  # Pydantic V2不可用，尝试V1
        except Exception as e:
            # TypeAdapter创建失败，尝试V1方法
            warnings.warn(f"Failed to create TypeAdapter: {e}, trying V1 approach", RuntimeWarning)

        # 尝试使用Pydantic V1的create_model_from_typeddict
        try:
            from pydantic.main import create_model_from_typeddict

            model = create_model_from_typeddict(typed_dict)
            return model
        except ImportError as e:
            raise ImportError(
                "Pydantic is required for get_pydantic_model_from_typed_dict(). "
                "Please install it with: pip install pydantic"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to create Pydantic model from TypedDict: {e}") from e

    def get_pydantic_model(self) -> Any:
        """获取或创建Pydantic模型（实例方法版本）

        优先使用TypeAdapter（Pydantic V2），如果不可用则使用create_model_from_typeddict（Pydantic V1）

        Returns:
            Pydantic模型实例

        Raises:
            ImportError: 如果Pydantic未安装
            RuntimeError: 如果无法创建Pydantic模型
        """
        if self._pydantic_model is not None:
            return self._pydantic_model

        self._pydantic_model = self.get_pydantic_model_from_typed_dict(self._typed_dict_class)
        return self._pydantic_model

    @classmethod
    def get_json_schema_from_typed_dict(cls, typed_dict: Type[Any]) -> Dict[str, Any]:
        """从TypedDict类型生成JSON Schema（类方法版本）

        Args:
            typed_dict: TypedDict类型定义

        Returns:
            JSON Schema字典

        Raises:
            ImportError: 如果Pydantic未安装
            RuntimeError: 如果无法生成JSON Schema
        """
        pydantic_model = cls.get_pydantic_model_from_typed_dict(typed_dict)

        try:
            schema: Dict[str, Any]
            # Pydantic V2 API
            if hasattr(pydantic_model, "json_schema"):
                # TypeAdapter的情况
                schema = pydantic_model.json_schema()
                return schema
            elif hasattr(pydantic_model, "model_json_schema"):
                # BaseModel的情况（V2）
                schema = pydantic_model.model_json_schema()
                return schema
            # Pydantic V1 API
            elif hasattr(pydantic_model, "schema"):
                schema = pydantic_model.schema()
                return schema
            else:
                raise RuntimeError("Unable to extract JSON schema from Pydantic model")
        except Exception as e:
            raise RuntimeError(f"Failed to generate JSON schema: {e}") from e

    def get_json_schema(self) -> Dict[str, Any]:
        """获取JSON Schema（实例方法版本，利用Pydantic转换）

        Returns:
            JSON Schema字典

        Raises:
            ImportError: 如果Pydantic未安装
            RuntimeError: 如果无法生成JSON Schema
        """
        if self._json_schema is not None:
            return self._json_schema

        self._json_schema = self.get_json_schema_from_typed_dict(self._typed_dict_class)
        return self._json_schema

    def export_to_envelope(self, **kwargs: Any) -> MessageEnvelope:
        """导出为统一信封字典

        将 typed_dict_class_module, typed_dict_class_name 和 json_schema 保存到 properties，
        确保 import_from_envelope 可以独立重建实例
        """
        base_dict = self.get_python_dict()

        # 尝试获取 json_schema（如果 Pydantic 可用）
        json_schema = None
        try:
            json_schema = self.get_json_schema()
        except (ImportError, RuntimeError):
            # Pydantic 不可用或生成失败，继续但不保存 schema
            pass

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

        # 将 typed_dict_class_module, typed_dict_class_name 和 json_schema 保存到 properties
        if "properties" not in envelope["metadata"]:
            envelope["metadata"]["properties"] = {}  # type: ignore[typeddict-item]
        envelope["metadata"]["properties"]["typed_dict_class_module"] = self.typed_dict_class_module  # type: ignore[typeddict-item]
        envelope["metadata"]["properties"]["typed_dict_class_name"] = self.typed_dict_class_name  # type: ignore[typeddict-item]
        if json_schema is not None:
            envelope["metadata"]["properties"]["json_schema"] = json_schema  # type: ignore[typeddict-item]

        return envelope

    @classmethod
    def import_from_envelope(cls, data: MessageEnvelope, **kwargs: Any) -> "TypedDictMessageInstance":
        """从规范信封创建TypedDict实例

        优先从 envelope.metadata.properties 读取 json_schema，
        如果没有 json_schema，则尝试从 typed_dict 参数或 typed_dict_class_path 恢复。

        Args:
            data: 消息信封
            **kwargs: 可选的'typed_dict'参数

        Returns:
            TypedDict实例

        Raises:
            ValueError: 如果无法确定TypedDict类型
        """
        content = data["content"]
        properties = data.get("metadata", {}).get("properties", {})

        # 优先从 kwargs 获取 typed_dict
        typed_dict = kwargs.pop("typed_dict", None)

        # 如果没有提供 typed_dict，尝试从 properties 恢复
        if typed_dict is None:
            typed_dict_class_module = properties.get("typed_dict_class_module")
            typed_dict_class_name = properties.get("typed_dict_class_name")

            if typed_dict_class_module and typed_dict_class_name:
                # 尝试从模块导入 TypedDict
                try:
                    import importlib

                    module = importlib.import_module(typed_dict_class_module)
                    typed_dict = getattr(module, typed_dict_class_name)
                except Exception as e:
                    raise ValueError(
                        f"Unable to import TypedDict '{typed_dict_class_name}' from module '{typed_dict_class_module}': {e}. "
                        "Please provide 'typed_dict' parameter explicitly."
                    ) from e

            if typed_dict is None:
                raise ValueError(
                    "Unable to determine TypedDict type. "
                    "Please provide 'typed_dict' parameter or ensure envelope contains valid type information "
                    "(typed_dict_class_module and typed_dict_class_name)."
                )

        instance = cls(content, typed_dict, **kwargs)
        return instance

    def get_python_dict(self) -> Dict[str, Any]:
        """获取当前所有的字段名和对应的原始值"""
        return self._typed_dict_data.copy()

    def set_python_dict(self, value: Dict[str, Any], **kwargs: Any) -> bool:
        """设置所有字段的值，只做已有字段的更新"""
        # 获取根访问器
        root_accessor = self._field_accessor
        if root_accessor is not None:
            root_accessor.update_from_dict(source_data=value)
        return True

    # TypeInfoProvider 接口实现
    def get_field_type_info(
        self, field_name: str, field_value: Any, parent_field_accessor: "FieldAccessor"
    ) -> Optional[TypeInfo]:
        """从TypedDict定义中提取字段类型信息

        Args:
            field_name: 字段名
            field_value: 字段值
            parent_field_accessor: 父级字段访问器

        Returns:
            字段的类型信息
        """
        # 构建完整路径
        full_path = f"{parent_field_accessor.full_path_from_root}.{field_name}"

        # 获取TypedDict的类型提示
        try:
            type_hints = get_type_hints(self._typed_dict_class)
        except Exception:
            type_hints = {}

        # 获取字段的类型注解
        field_type_annotation = type_hints.get(field_name)

        # 确定类型信息
        python_type = type(field_value)
        if field_type_annotation is not None:
            # 从类型注解推断标准类型
            standard_type = TypeConverter.python_type_to_standard(field_type_annotation)
        else:
            # 如果没有类型注解，从值的类型推断
            standard_type = TypeConverter.python_type_to_standard(python_type)

        # 创建基础TypeInfo
        type_info = TypeInfo(
            field_name=field_name,
            field_path=full_path,
            standard_type=standard_type,
            python_type=python_type,
            original_type=field_type_annotation if field_type_annotation is not None else python_type,
            current_value=field_value,
        )

        # 检查字段是否为必需字段
        if hasattr(self._typed_dict_class, "__required_keys__"):
            required_keys = getattr(self._typed_dict_class, "__required_keys__")
            if field_name in required_keys:
                type_info.add_constraint(
                    ConstraintType.REQUIRED,
                    True,
                    "Field is required by TypedDict definition",
                )

        # 处理列表/数组类型
        if isinstance(field_value, list):
            type_info.is_array = True
            # 可以进一步提取元素类型信息，但这需要更复杂的类型解析
            # 暂时留给后续版本实现

        # 处理字典/对象类型
        elif isinstance(field_value, dict):
            type_info.is_object = True
            # 可以进一步提取对象字段信息，但这需要递归解析
            # 暂时留给后续版本实现

        return type_info
