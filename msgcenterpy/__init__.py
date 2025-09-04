"""
MsgCenterPy - Unified Message Conversion System

A multi-format message conversion system supporting seamless conversion
between ROS2, Pydantic, Dataclass, JSON, Dict, YAML and JSON Schema.
"""

__version__ = "0.1.0"
__license__ = "Apache-2.0"

from msgcenterpy.core.envelope import MessageEnvelope, create_envelope
from msgcenterpy.core.field_accessor import FieldAccessor
from msgcenterpy.core.message_center import MessageCenter

# Core imports
from msgcenterpy.core.message_instance import MessageInstance
from msgcenterpy.core.type_converter import StandardType, TypeConverter
from msgcenterpy.core.type_info import ConstraintType, TypeInfo
from msgcenterpy.core.types import ConversionError, MessageType, ValidationError

# Always available instance
from msgcenterpy.instances.json_schema_instance import JSONSchemaMessageInstance

# Optional ROS2 instance (with graceful fallback)
try:
    from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

    _HAS_ROS2 = True
except ImportError:
    _HAS_ROS2 = False


# Convenience function
def get_message_center() -> MessageCenter:
    """Get the MessageCenter singleton instance."""
    return MessageCenter.get_instance()


# Main exports
__all__ = [
    # Version info
    "__version__",
    "__license__",
]


def get_version() -> str:
    """Get the current version of MsgCenterPy."""
    return __version__


def get_package_info() -> dict:
    """Get package information."""
    return {
        "name": "msgcenterpy",
        "version": __version__,
        "description": "Unified message conversion system supporting ROS2, Pydantic, Dataclass, JSON, YAML, Dict, and JSON Schema inter-conversion",
        "license": __license__,
        "url": "https://github.com/ZGCA-Forge/MsgCenterPy",
        "keywords": [
            "message",
            "conversion",
            "ros2",
            "pydantic",
            "dataclass",
            "json",
            "yaml",
            "mcp",
        ],
    }


def check_dependencies() -> dict:
    """Check which optional dependencies are available."""
    dependencies = {
        "ros2": False,
        "jsonschema": False,
    }

    # Check ROS2
    try:
        import rclpy  # type: ignore
        import rosidl_runtime_py  # type: ignore

        dependencies["ros2"] = True
    except ImportError:
        pass

    # Check jsonschema
    try:
        import jsonschema  # type: ignore

        dependencies["jsonschema"] = True
    except ImportError:
        pass

    return dependencies
