from typing import Any, Dict, Optional, Type

from msgcenterpy.core.envelope import MessageEnvelope, Properties
from msgcenterpy.core.message_instance import MessageInstance
from msgcenterpy.core.types import MessageType


class MessageCenter:
    """Message Center singleton class that manages all message types and instances"""

    _instance: Optional["MessageCenter"] = None

    @classmethod
    def get_instance(cls) -> "MessageCenter":
        """Get MessageCenter singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """Private constructor, use get_instance() to get singleton"""
        self._type_registry: Dict[MessageType, Type[MessageInstance]] = {}
        self._register_builtin_types()

    def _register_builtin_types(self) -> None:
        """Register built-in message types with lazy import to avoid circular dependencies"""
        try:
            from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

            self._type_registry[MessageType.ROS2] = ROS2MessageInstance
        except ImportError:
            pass
        try:
            from msgcenterpy.instances.json_schema_instance import (
                JSONSchemaMessageInstance,
            )

            self._type_registry[MessageType.JSON_SCHEMA] = JSONSchemaMessageInstance
        except ImportError:
            pass

    def get_instance_class(self, message_type: MessageType) -> Type[MessageInstance]:
        """Get instance class for the specified message type"""
        instance_class = self._type_registry.get(message_type)
        if not instance_class:
            raise ValueError(f"Unsupported message type: {message_type}")
        return instance_class

    def convert(
        self,
        source: MessageInstance,
        target_type: MessageType,
        override_properties: Dict[str, Any],
        **kwargs: Any,
    ) -> MessageInstance:
        """Convert message types"""
        target_class = self.get_instance_class(target_type)
        dict_data: MessageEnvelope = source.export_to_envelope()
        if "properties" not in dict_data["metadata"]:
            dict_data["metadata"]["properties"] = Properties()
        dict_data["metadata"]["properties"].update(override_properties)  # type: ignore[typeddict-item]
        target_instance = target_class.import_from_envelope(dict_data)
        return target_instance


# Module-level convenience function using singleton
def get_message_center() -> MessageCenter:
    """Get message center singleton"""
    return MessageCenter.get_instance()
