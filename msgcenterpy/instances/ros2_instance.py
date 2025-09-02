import array
import importlib
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from rosidl_parser.definition import NamespacedType  # type: ignore
from rosidl_runtime_py import (  # type: ignore
    import_message_from_namespaced_type,
    message_to_ordereddict,
    set_message_fields,
)

from msgcenterpy.core.envelope import MessageEnvelope, create_envelope
from msgcenterpy.core.message_instance import MessageInstance
from msgcenterpy.core.type_converter import TypeConverter
from msgcenterpy.core.type_info import ConstraintType, Consts, TypeInfo
from msgcenterpy.core.types import MessageType

if TYPE_CHECKING:
    from msgcenterpy.core.field_accessor import FieldAccessor


class ROS2MessageInstance(MessageInstance[Any]):
    """ROS2消息实例，支持类型信息提取和字段访问器"""

    ros_msg_cls: Type[Any] = None  # type: ignore

    @classmethod
    def get_ros_msg_cls_path(cls, ros_msg_cls: Type[Any]) -> str:
        return ros_msg_cls.__module__ + "." + ros_msg_cls.__name__

    @property
    def ros_msg_cls_path(self) -> str:
        return self.get_ros_msg_cls_path(self.ros_msg_cls)

    @classmethod
    def get_ros_msg_cls_namespace(cls, ros_msg_cls: Type[Any]) -> str:
        class_name, module_name = ros_msg_cls.__name__, ros_msg_cls.__module__
        package = module_name.split(".")[0] if module_name else ""
        interface = (
            "msg"
            if ".msg" in module_name
            else "srv"
            if ".srv" in module_name
            else "action"
            if ".action" in module_name
            else "msg"
        )
        return f"{package}/{interface}/{class_name}" if package and class_name else f"{module_name}.{class_name}"

    @property
    def ros_msg_cls_namespace(self) -> str:
        return self.get_ros_msg_cls_namespace(self.ros_msg_cls)

    @classmethod
    def obtain_ros_cls_from_str(cls, message_type: str | Type[Any]) -> Type[Any]:
        # 需要先解析出正确的消息类
        if isinstance(message_type, str):
            if "/" in message_type:
                namespace, name = message_type.rsplit("/", 1)
                message_type = import_message_from_namespaced_type(NamespacedType(namespace.split("/"), name))
            elif "." in message_type:
                module_path, class_name = message_type.rsplit(".", 1)
                mod = importlib.import_module(module_path)
                message_type = getattr(mod, class_name)
        return message_type  # type: ignore

    def __init__(self, inner_data: Any, **kwargs: Any) -> None:
        self.ros_msg_cls = inner_data.__class__
        if not isinstance(self.ros_msg_cls, type):
            raise TypeError(f"Expected ROS message class to be a type, got {type(self.ros_msg_cls)}")
        super().__init__(inner_data, MessageType.ROS2)

    def export_to_envelope(self, **kwargs: Any) -> MessageEnvelope:
        """导出为统一信封字典

        用户可从 metadata.properties 中读取：
        - properties.ros_msg_cls_namespace
        - properties.ros_msg_cls_path
        """
        base_dict = self.get_python_dict()
        export_envelope = create_envelope(
            format_name=self.message_type.value,
            content=base_dict,
            metadata={
                "current_format": self.message_type.value,
                "source_cls_name": self.inner_data.__class__.__name__,
                "source_cls_module": self.inner_data.__class__.__module__,
                **self._metadata,
            },
        )
        return export_envelope

    @classmethod
    def _ordered_to_dict(cls, obj: Any) -> Any:
        if isinstance(obj, OrderedDict):
            return {k: cls._ordered_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, tuple):
            return tuple(cls._ordered_to_dict(v) for v in obj)
        elif isinstance(obj, (list, array.array)):
            return [cls._ordered_to_dict(v) for v in obj]
        else:
            return obj

    @classmethod
    def import_from_envelope(cls, data: MessageEnvelope, **kwargs: Any) -> "ROS2MessageInstance":
        """从规范信封创建ROS2实例（仅 data 一个参数）。

        类型信息从 data.metadata.properties 读取
        """
        content = data["content"]
        properties = data["metadata"]["properties"]
        ros_msg_cls = cls.obtain_ros_cls_from_str(properties["ros_msg_cls_namespace"]) or cls.obtain_ros_cls_from_str(
            properties["ros_msg_cls_path"]
        )
        if ros_msg_cls is None:
            raise ValueError(
                "ros2 type must be provided via metadata.properties.ros_msg_cls_namespace or legacy type_info.ros_namespaced"
            )
        ros_msg = ros_msg_cls()
        set_message_fields(ros_msg, content)
        instance = ROS2MessageInstance(ros_msg)
        return instance

    def get_python_dict(self) -> Dict[str, Any]:
        """获取当前所有的字段名和对应的原始值，使用 SLOT_TYPES 进行类型推断和嵌套导入"""
        base_obj = message_to_ordereddict(self.inner_data)
        base_dict = self._ordered_to_dict(base_obj)
        return base_dict  # type: ignore[no-any-return]

    def set_python_dict(self, value: Dict[str, Any], **kwargs: Any) -> bool:
        """获取当前所有的字段名和对应的原始值，使用 SLOT_TYPES 进行类型推断和嵌套导入"""
        timestamp_fields = set_message_fields(self.inner_data, value, **kwargs)
        # todo: 因为ROS自身机制，字段并不会增减，所以需要更新cache中所有accessor的值（通过parent获取）
        return True

    # TypeInfoProvider 接口实现
    def get_field_type_info(
        self, field_name: str, field_value: Any, parent_field_accessor: "FieldAccessor"
    ) -> Optional[TypeInfo]:
        """从ROS2消息定义中提取字段类型信息

        使用 ROS 消息的 SLOT_TYPES 获取精确的类型信息，并通过 TypeConverter 转换为标准类型
        """
        # 通过 parent_field_accessor 获取 ROS 消息实例
        ros_msg_instance = parent_field_accessor.value

        # 构建完整路径用于TypeInfo
        full_path = f"{parent_field_accessor.full_path_from_root}.{field_name}"

        # noinspection PyProtectedMember
        slots = ros_msg_instance._fields_and_field_types
        slot_types = ros_msg_instance.SLOT_TYPES

        # 通过 zip 找到 field_name 对应的类型定义
        ros_definition_type = None
        for slot_name, slot_type in zip(slots, slot_types):
            if slot_name == field_name:
                ros_definition_type = slot_type
                break

        if ros_definition_type is None:
            raise ValueError(f"Field '{field_name}' not found in ROS message slots")

        # 使用 TypeConverter 转换为标准类型
        standard_type = TypeConverter.rosidl_definition_to_standard(ros_definition_type)

        # 创建 TypeInfo
        type_info = TypeInfo(
            field_name=field_name,
            field_path=full_path,
            standard_type=standard_type,
            python_type=type(field_value),
            original_type=ros_definition_type,
        )
        type_info.current_value = field_value

        # 从 rosidl 定义中提取详细类型信息（约束、数组信息等）
        self._extract_from_rosidl_definition(type_info)

        return type_info

    def _extract_from_rosidl_definition(self, type_info: TypeInfo) -> None:
        """从rosidl_parser定义中提取详细类型信息

        Args:
            type_info: 要填充的TypeInfo对象
        """
        from rosidl_parser.definition import (
            AbstractNestedType,
            Array,
            BasicType,
            BoundedSequence,
            BoundedString,
            BoundedWString,
            NamespacedType,
            UnboundedSequence,
        )

        # 从type_info获取所需信息
        definition_type = type_info.original_type

        get_element_type = False
        # 提取约束信息
        if isinstance(definition_type, (BoundedString, BoundedWString)):
            type_info.add_constraint(ConstraintType.MAX_LENGTH, definition_type.maximum_size)
        elif isinstance(definition_type, Array):
            type_info.is_array = True
            type_info.array_size = definition_type.size
            type_info.add_constraint(ConstraintType.MIN_ITEMS, definition_type.size)
            type_info.add_constraint(ConstraintType.MAX_ITEMS, definition_type.size)
            get_element_type = True
        elif isinstance(definition_type, BoundedSequence):
            type_info.is_array = True
            type_info.add_constraint(ConstraintType.MAX_ITEMS, definition_type.maximum_size)
            get_element_type = True
        elif isinstance(definition_type, UnboundedSequence):
            type_info.is_array = True
            get_element_type = True
        elif isinstance(definition_type, BasicType):
            # 基础类型的约束将在 field_accessor 中自动添加
            pass
        elif isinstance(definition_type, NamespacedType):
            # 对象类型，标记为对象并提取字段信息
            type_info.is_object = True
            type_info.add_constraint(ConstraintType.TYPE_KEEP, True)
            # 这里可以进一步扩展来提取对象字段信息
        # 提取元素类型信息
        if get_element_type:
            if not isinstance(definition_type, AbstractNestedType):
                raise TypeError(f"Expected AbstractNestedType for element type extraction, got {type(definition_type)}")
            # 创建元素类型的TypeInfo并递归填充
            std_type = TypeConverter.rosidl_definition_to_standard(definition_type.value_type)
            python_type = TypeConverter.standard_to_python_type(std_type)
            type_info.element_type_info = TypeInfo(
                field_name=Consts.ELEMENT_TYPE_INFO_SYMBOL,
                field_path=Consts.ELEMENT_TYPE_INFO_SYMBOL,
                standard_type=std_type,
                python_type=python_type,
                original_type=definition_type.value_type,
            )
            self._extract_from_rosidl_definition(type_info.element_type_info)
