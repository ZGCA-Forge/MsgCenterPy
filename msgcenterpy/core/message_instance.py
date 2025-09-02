import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Type, TypeVar, cast

from msgcenterpy.core.envelope import FormatMetadata, MessageEnvelope, Properties
from msgcenterpy.core.field_accessor import (
    FieldAccessor,
    FieldAccessorFactory,
    TypeInfoProvider,
)
from msgcenterpy.core.types import MessageType

if TYPE_CHECKING:
    # 仅用于类型检查的导入，避免运行时循环依赖
    from msgcenterpy.instances.json_schema_instance import JSONSchemaMessageInstance
    from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

T = TypeVar("T")


class MessageInstance(TypeInfoProvider, ABC, Generic[T]):
    """统一消息实例基类"""

    _init_ok: bool = False

    # 字段访问器相关方法
    @property
    def fields(self) -> FieldAccessor:
        if self._field_accessor is None:
            raise RuntimeError("FieldAccessor not initialized")
        return self._field_accessor

    def __setattr__(self, field_name: str, value: Any) -> None:
        if not self._init_ok:
            return super().__setattr__(field_name, value)
        for cls in self.__class__.__mro__:
            if field_name in cls.__dict__:
                return super().__setattr__(field_name, value)
        self.fields[field_name] = value
        return None

    def __getattr__(self, field_name: str) -> Any:
        if not self._init_ok:
            return super().__getattribute__(field_name)
        for cls in self.__class__.__mro__:
            if field_name in cls.__dict__:
                return super().__getattribute__(field_name)
        return self.fields[field_name]

    def __getitem__(self, field_name: str) -> Any:
        """支持通过下标访问字段"""
        return self.fields[field_name]

    def __setitem__(self, field_name: str, value: Any) -> None:
        """支持通过下标设置字段"""
        self.fields[field_name] = value

    def __contains__(self, field_name: str) -> bool:
        """支持in操作符检查字段是否存在"""
        return field_name in self.fields

    def __init__(
        self,
        inner_data: T,
        message_type: MessageType,
        metadata: Optional[FormatMetadata] = None,
    ):
        # 初始化标记和基础属性
        self._field_accessor: Optional[FieldAccessor] = None

        self._instance_id: str = str(uuid.uuid4())
        self.inner_data: T = inner_data  # 原始类型数据
        self.message_type: MessageType = message_type
        self._metadata: FormatMetadata = metadata or FormatMetadata()
        self._created_at = datetime.now(timezone.utc)
        self._collect_public_properties_to_metadata()
        self._field_accessor = FieldAccessorFactory.create_accessor(self.inner_data, self)
        self._init_ok = True

    def _collect_public_properties_to_metadata(self) -> None:
        """将所有非下划线开头的 @property 的当前值放入 metadata.properties 中。

        仅收集只读属性，忽略访问抛出异常的属性。
        """
        properties_bucket = self._metadata.setdefault("properties", Properties())
        for cls in self.__class__.__mro__:
            for attribute_name, attribute_value in cls.__dict__.items():
                if attribute_name.startswith("_"):
                    continue
                if isinstance(attribute_value, property):
                    try:
                        # 避免重复收集已存在的属性
                        if attribute_name not in properties_bucket:
                            properties_bucket[attribute_name] = getattr(self, attribute_name)  # type: ignore[literal-required]
                    except (AttributeError, TypeError, RuntimeError):
                        # Skip attributes that can't be accessed or have incompatible types
                        # This includes attributes that require initialization to complete (like 'fields')
                        pass

    def to(self, target_type: MessageType, **kwargs: Any) -> "MessageInstance[Any]":
        """直接转换到目标类型"""
        if target_type == MessageType.ROS2:
            return cast("MessageInstance[Any]", self.to_ros2(**kwargs))
        elif target_type == MessageType.DICT:
            return cast("MessageInstance[Any]", self.to_dict(**kwargs))
        elif target_type == MessageType.JSON:
            return cast("MessageInstance[Any]", self.to_json(**kwargs))
        elif target_type == MessageType.JSON_SCHEMA:
            return cast("MessageInstance[Any]", self.to_json_schema(**kwargs))
        elif target_type == MessageType.YAML:
            return cast("MessageInstance[Any]", self.to_yaml(**kwargs))
        elif target_type == MessageType.PYDANTIC:
            return cast("MessageInstance[Any]", self.to_pydantic(**kwargs))
        elif target_type == MessageType.DATACLASS:
            return cast("MessageInstance[Any]", self.to_dataclass(**kwargs))
        else:
            raise ValueError(f"Unsupported target message type: {target_type}")

    @classmethod
    @abstractmethod
    def import_from_envelope(cls, data: MessageEnvelope, **kwargs: Any) -> "MessageInstance[Any]":
        """从统一信封字典创建实例（仅接受 data 一个参数）。"""
        # metadata会被重置
        pass

    @abstractmethod
    def export_to_envelope(self, **kwargs: Any) -> MessageEnvelope:
        """导出为字典格式"""
        pass

    @abstractmethod
    def get_python_dict(self) -> Dict[str, Any]:
        """获取当前所有的字段名和对应的python可读值"""
        pass

    @abstractmethod
    def set_python_dict(self, value: Dict[str, Any], **kwargs: Any) -> bool:
        """设置所有字段的值"""
        pass

    def get_json_schema(self) -> Dict[str, Any]:
        """生成当前消息实例的JSON Schema，委托给FieldAccessor递归处理"""
        # 直接调用FieldAccessor的get_json_schema方法
        schema = self.fields.get_json_schema()

        # 添加schema元信息（对于JSONSchemaMessageInstance，如果已有title则保持，否则添加默认title）
        from msgcenterpy.instances.json_schema_instance import JSONSchemaMessageInstance

        if isinstance(self, JSONSchemaMessageInstance):
            # 对于JSON Schema实例，如果schema中没有title，则添加一个
            if "title" not in schema:
                schema["title"] = f"{self.__class__.__name__} Schema"  # type: ignore
            if "description" not in schema:
                schema["description"] = f"JSON Schema generated from {self.message_type.value} message instance"  # type: ignore
        else:
            # 对于其他类型的实例，总是添加schema元信息
            schema["title"] = f"{self.__class__.__name__} Schema"  # type: ignore
            schema["description"] = f"JSON Schema generated from {self.message_type.value} message instance"  # type: ignore

        return schema

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.message_type.value}, id={self._instance_id[:8]})"

    # 便捷转换方法，使用MessageCenter单例
    def to_ros2(self, type_hint: str | Type[Any], **kwargs: Any) -> "ROS2MessageInstance":
        """转换到ROS2实例。传入必备的类型提示，"""
        override_properties = {}
        from msgcenterpy.core.message_center import get_message_center

        ros2_message_instance = cast(
            ROS2MessageInstance,
            get_message_center().get_instance_class(MessageType.ROS2),
        )
        ros_type = ros2_message_instance.obtain_ros_cls_from_str(type_hint)
        override_properties["ros_msg_cls_path"] = ROS2MessageInstance.get_ros_msg_cls_path(ros_type)
        override_properties["ros_msg_cls_namespace"] = ROS2MessageInstance.get_ros_msg_cls_namespace(ros_type)
        return cast(
            ROS2MessageInstance,
            get_message_center().convert(self, MessageType.ROS2, override_properties, **kwargs),
        )

    def to_json_schema(self, **kwargs: Any) -> "JSONSchemaMessageInstance":
        """转换到JSON Schema实例"""
        override_properties = {"json_schema": self.get_json_schema()}
        from msgcenterpy.core.message_center import get_message_center
        from msgcenterpy.instances.json_schema_instance import JSONSchemaMessageInstance

        return cast(
            JSONSchemaMessageInstance,
            get_message_center().convert(self, MessageType.JSON_SCHEMA, override_properties, **kwargs),
        )
