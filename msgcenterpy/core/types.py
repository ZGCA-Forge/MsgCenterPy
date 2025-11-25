from enum import Enum


class MessageType(Enum):
    """Supported message types"""

    ROS2 = "ros2"
    PYDANTIC = "pydantic"
    DATACLASS = "dataclass"
    JSON = "json"
    JSON_SCHEMA = "json_schema"
    DICT = "dict"
    YAML = "yaml"
    TYPED_DICT = "typed_dict"  # Experimental


class ConversionError(Exception):
    """Conversion error exception"""

    pass


class ValidationError(Exception):
    """Validation error exception"""

    pass
