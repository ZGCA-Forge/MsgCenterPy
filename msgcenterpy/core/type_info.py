import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from msgcenterpy.core.type_converter import StandardType, TypeConverter


class Consts:
    ELEMENT_TYPE_INFO_SYMBOL = "ELEMENT_TYPE_INFO"
    ACCESSOR_ROOT_NODE = "MSG_CENTER_ROOT"


class ConstraintType(Enum):
    """Constraint type enumeration"""

    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_ITEMS = "min_items"
    MAX_ITEMS = "max_items"
    PATTERN = "pattern"
    ENUM_VALUES = "enum_values"
    MULTIPLE_OF = "multiple_of"
    TYPE_KEEP = "type_keep"
    EXCLUSIVE_MIN = "exclusive_min"
    EXCLUSIVE_MAX = "exclusive_max"
    UNIQUE_ITEMS = "unique_items"
    DEFAULT_VALUE = "default_value"
    REQUIRED = "required"
    FORMAT = "format"


@dataclass
class TypeConstraint:
    """Type constraint definition"""

    type: ConstraintType
    value: Any
    description: Optional[str] = None

    def to_json_schema_property(self) -> Dict[str, Any]:
        """Convert to JSON Schema property"""
        mapping = {
            ConstraintType.MIN_VALUE: "minimum",
            ConstraintType.MAX_VALUE: "maximum",
            ConstraintType.MIN_LENGTH: "minLength",
            ConstraintType.MAX_LENGTH: "maxLength",
            ConstraintType.MIN_ITEMS: "minItems",
            ConstraintType.MAX_ITEMS: "maxItems",
            ConstraintType.PATTERN: "pattern",
            ConstraintType.ENUM_VALUES: "enum",
            ConstraintType.MULTIPLE_OF: "multipleOf",
            ConstraintType.EXCLUSIVE_MIN: "exclusiveMinimum",
            ConstraintType.EXCLUSIVE_MAX: "exclusiveMaximum",
            ConstraintType.UNIQUE_ITEMS: "uniqueItems",
            ConstraintType.DEFAULT_VALUE: "default",
            ConstraintType.FORMAT: "format",
        }

        property_name = mapping.get(self.type)
        if property_name:
            result = {property_name: self.value}
            if self.description:
                result["description"] = self.description
            return result
        return {}


@dataclass
class TypeInfo:
    """Detailed type information including standard type, Python type and constraints"""

    # Basic type information
    field_name: str
    field_path: str
    standard_type: StandardType
    python_type: Type
    original_type: Any  # Original type (e.g., ROS2 type instance)
    _outdated: bool = False

    @property
    def outdated(self) -> bool:
        return self._outdated

    # Value information
    current_value: Any = None
    default_value: Any = None

    # Constraints
    constraints: List[TypeConstraint] = field(default_factory=list)

    # Array/sequence related information
    is_array: bool = False
    array_size: Optional[int] = None  # Fixed size array
    _element_type_info: Optional["TypeInfo"] = None  # Array element type

    @property
    def element_type_info(self) -> Optional["TypeInfo"]:
        return self._element_type_info

    @element_type_info.setter
    def element_type_info(self, value: Optional["TypeInfo"]) -> None:
        if self.outdated:
            raise ValueError("Should not change an outdated type")
        if value is not None:
            value.field_name = Consts.ELEMENT_TYPE_INFO_SYMBOL
            value.field_path = Consts.ELEMENT_TYPE_INFO_SYMBOL
        self._element_type_info = value

    # Object related information
    is_object: bool = False
    object_fields: Dict[str, "TypeInfo"] = field(default_factory=dict)

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def python_value_from_standard_type(self) -> Any:
        return TypeConverter.convert_to_python_value_with_standard_type(self.current_value, self.standard_type)

    def add_constraint(
        self,
        constraint_type: ConstraintType,
        value: Any,
        description: Optional[str] = None,
    ) -> None:
        """Add constraint"""
        constraint = TypeConstraint(constraint_type, value, description)
        # Avoid duplicate constraints of the same type
        self.constraints = [c for c in self.constraints if c.type != constraint_type]
        self.constraints.append(constraint)

    def get_constraint(self, constraint_type: ConstraintType) -> Optional[TypeConstraint]:
        """Get constraint of specified type"""
        for constraint in self.constraints:
            if constraint.type == constraint_type:
                return constraint
        return None

    def has_constraint(self, constraint_type: ConstraintType) -> bool:
        """Check if constraint of specified type exists"""
        return self.get_constraint(constraint_type) is not None

    def get_constraint_value(self, constraint_type: ConstraintType) -> Any:
        """Get value of specified constraint"""
        constraint = self.get_constraint(constraint_type)
        return constraint.value if constraint else None

    def validate_value(self, value: Any) -> bool:
        """Validate value according to constraints"""
        try:
            if self.get_constraint(ConstraintType.TYPE_KEEP):
                # ROS includes TYPE_KEEP
                if type(self.current_value) != type(value):
                    return False
            # Basic type check
            if not self._validate_basic_type(value):
                return False

            # Numeric constraint check
            if not self._validate_numeric_constraints(value):
                return False

            # String constraint check
            if not self._validate_string_constraints(value):
                return False

            # Array constraint check
            if not self._validate_array_constraints(value):
                return False

            return True

        except Exception:
            return False

    def _validate_basic_type(self, value: Any) -> bool:
        """Validate basic type"""
        if value is None:
            return not self.has_constraint(ConstraintType.REQUIRED)
        return True

    def _validate_numeric_constraints(self, value: Any) -> bool:
        """Validate numeric constraints"""
        if not isinstance(value, (int, float)):
            return True

        min_val = self.get_constraint_value(ConstraintType.MIN_VALUE)
        if min_val is not None and value < min_val:
            return False

        max_val = self.get_constraint_value(ConstraintType.MAX_VALUE)
        if max_val is not None and value > max_val:
            return False

        exclusive_min = self.get_constraint_value(ConstraintType.EXCLUSIVE_MIN)
        if exclusive_min is not None and value <= exclusive_min:
            return False

        exclusive_max = self.get_constraint_value(ConstraintType.EXCLUSIVE_MAX)
        if exclusive_max is not None and value >= exclusive_max:
            return False

        multiple_of = self.get_constraint_value(ConstraintType.MULTIPLE_OF)
        if multiple_of is not None and value % multiple_of != 0:
            return False

        return True

    def _validate_string_constraints(self, value: Any) -> bool:
        """Validate string constraints"""
        if not isinstance(value, str):
            return True

        min_len = self.get_constraint_value(ConstraintType.MIN_LENGTH)
        if min_len is not None and len(value) < min_len:
            return False

        max_len = self.get_constraint_value(ConstraintType.MAX_LENGTH)
        if max_len is not None and len(value) > max_len:
            return False

        pattern = self.get_constraint_value(ConstraintType.PATTERN)
        if pattern is not None:
            import re

            if not re.match(pattern, value):
                return False

        enum_values = self.get_constraint_value(ConstraintType.ENUM_VALUES)
        if enum_values is not None and value not in enum_values:
            return False

        return True

    def _validate_array_constraints(self, value: Any) -> bool:
        """Validate array constraints"""
        if not isinstance(value, (list, tuple)):
            return True

        min_items = self.get_constraint_value(ConstraintType.MIN_ITEMS)
        if min_items is not None and len(value) < min_items:
            return False

        max_items = self.get_constraint_value(ConstraintType.MAX_ITEMS)
        if max_items is not None and len(value) > max_items:
            return False

        if self.array_size is not None and len(value) != self.array_size:
            return False

        unique_items = self.get_constraint_value(ConstraintType.UNIQUE_ITEMS)
        if unique_items and len(set(value)) != len(value):
            return False

        return True

    def to_json_schema_property(self, include_constraints: bool = True) -> Dict[str, Any]:
        """Convert to JSON Schema property definition"""
        from msgcenterpy.core.type_converter import TypeConverter

        # Basic properties
        property_schema: Dict[str, Any] = {"type": TypeConverter.standard_type_to_json_schema_type(self.standard_type)}

        # Add constraints
        if include_constraints:
            for constraint in self.constraints:
                constraint_props = constraint.to_json_schema_property()
                property_schema.update(constraint_props)

        # Special handling for array types
        if self.is_array and self.element_type_info:
            property_schema["items"] = self.element_type_info.to_json_schema_property(include_constraints)

        # Special handling for object types
        if self.is_object and self.object_fields:
            properties = {}
            for field_name, field_info in self.object_fields.items():
                properties[field_name] = field_info.to_json_schema_property(include_constraints)
            property_schema["properties"] = properties

        # Add description
        if self.original_type:
            property_schema["description"] = f"Field of type {self.original_type}"

        return property_schema

    def convert_value(self, value: Any, target_standard_type: Optional[StandardType] = None) -> Any:
        """Convert value to current type or specified target type"""
        target_type = target_standard_type or self.standard_type
        converted_value = TypeConverter.convert_to_python_value_with_standard_type(value, target_type)
        # Validate converted value
        if target_standard_type is None and not self.validate_value(converted_value):
            # Format constraint information
            constraints_info = []
            for c in self.constraints:
                constraint_desc = f"{c.type.value}: {c.value}"
                if c.description:
                    constraint_desc += f" ({c.description})"
                constraints_info.append(constraint_desc)

            constraints_str = ", ".join(constraints_info) if constraints_info else "No constraints"
            raise ValueError(
                f"Value {value} does not meet constraints for field {self.field_name}. "
                f"Constraints: [{constraints_str}]"
            )
        return converted_value

    def get_value_info(self) -> Dict[str, Any]:
        """Get detailed information about current value"""
        return {
            "field_name": self.field_name,
            "current_value": self.current_value,
            "standard_type": self.standard_type.value,
            "python_type": self.python_type.__name__,
            "original_type": self.original_type,
            "is_valid": self.validate_value(self.current_value),
            "constraints": [
                {"type": c.type.value, "value": c.value, "description": c.description} for c in self.constraints
            ],
            "is_array": self.is_array,
            "array_size": self.array_size,
            "is_object": self.is_object,
            "metadata": self.metadata,
        }

    def clone(self) -> "TypeInfo":
        """Create deep copy of TypeInfo"""
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        constraints_str = f", {len(self.constraints)} constraints" if self.constraints else ""
        return f"TypeInfo({self.field_name}: {self.standard_type.value}{constraints_str})"


class TypeInfoPostProcessor:
    """TypeInfo post-processor that adds default constraints to TypeInfo"""

    @staticmethod
    def add_basic_type_constraints(type_info: TypeInfo) -> None:
        """Add range constraints for basic types"""
        if not type_info.standard_type:
            return

        standard_type = type_info.standard_type

        # Integer type range constraints
        if standard_type == StandardType.INT8:
            type_info.add_constraint(ConstraintType.MIN_VALUE, -128)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 127)
        elif standard_type in (
            StandardType.UINT8,
            StandardType.BYTE,
            StandardType.OCTET,
        ):
            type_info.add_constraint(ConstraintType.MIN_VALUE, 0)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 255)
        elif standard_type == StandardType.INT16:
            type_info.add_constraint(ConstraintType.MIN_VALUE, -32768)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 32767)
        elif standard_type == StandardType.UINT16:
            type_info.add_constraint(ConstraintType.MIN_VALUE, 0)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 65535)
        elif standard_type == StandardType.INT32:
            type_info.add_constraint(ConstraintType.MIN_VALUE, -2147483648)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 2147483647)
        elif standard_type == StandardType.UINT32:
            type_info.add_constraint(ConstraintType.MIN_VALUE, 0)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 4294967295)
        elif standard_type == StandardType.INT64:
            type_info.add_constraint(ConstraintType.MIN_VALUE, -9223372036854775808)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 9223372036854775807)
        elif standard_type == StandardType.UINT64:
            type_info.add_constraint(ConstraintType.MIN_VALUE, 0)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 18446744073709551615)
        # Floating point type range constraints
        elif standard_type in (StandardType.FLOAT, StandardType.FLOAT32):
            type_info.add_constraint(ConstraintType.MIN_VALUE, -3.4028235e38)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 3.4028235e38)
        elif standard_type in (StandardType.DOUBLE, StandardType.FLOAT64):
            type_info.add_constraint(ConstraintType.MIN_VALUE, -1.7976931348623157e308)
            type_info.add_constraint(ConstraintType.MAX_VALUE, 1.7976931348623157e308)

    @staticmethod
    def add_default_constraints(type_info: TypeInfo) -> None:
        """Add default constraints"""
        field_value = type_info.current_value

        # Add constraints for array types
        if isinstance(field_value, (list, tuple)):
            type_info.is_array = True
            # 不再添加冗余的 MIN_ITEMS: 0

    @staticmethod
    def post_process_type_info(type_info: TypeInfo) -> None:
        """Post-process TypeInfo, adding various default constraints"""
        TypeInfoPostProcessor.add_basic_type_constraints(type_info)
        TypeInfoPostProcessor.add_default_constraints(type_info)
