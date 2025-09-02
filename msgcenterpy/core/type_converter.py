from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Type, Union, get_args, get_origin


class StandardType(Enum):
    """标准化的数据类型，用于不同数据源之间的转换

    增强版本，提供更细粒度的类型保留以更好地保存原始类型信息
    """

    # 基础类型
    STRING = "string"  # 字符串类型
    WSTRING = "wstring"  # 宽字符串类型
    CHAR = "char"  # 字符类型
    WCHAR = "wchar"  # 宽字符类型

    # 整数类型（细分以保留精度信息）
    INT8 = "int8"  # 8位有符号整数
    UINT8 = "uint8"  # 8位无符号整数
    INT16 = "int16"  # 16位有符号整数
    UINT16 = "uint16"  # 16位无符号整数
    INT32 = "int32"  # 32位有符号整数
    UINT32 = "uint32"  # 32位无符号整数
    INT64 = "int64"  # 64位有符号整数
    UINT64 = "uint64"  # 64位无符号整数
    INTEGER = "integer"  # 通用整数类型（向后兼容）
    BYTE = "byte"  # 字节类型
    OCTET = "octet"  # 八位字节类型

    # 浮点类型（细分以保留精度信息）
    FLOAT32 = "float32"  # 32位浮点数
    FLOAT64 = "float64"  # 64位浮点数（双精度）
    DOUBLE = "double"  # 双精度浮点数
    FLOAT = "float"  # 通用浮点类型（向后兼容）

    # 布尔类型
    BOOLEAN = "boolean"  # 布尔类型
    BOOL = "bool"  # 布尔类型（ROS2风格）

    # 空值类型
    NULL = "null"  # 空值类型

    # 容器类型
    ARRAY = "array"  # 数组/序列类型
    BOUNDED_ARRAY = "bounded_array"  # 有界数组类型
    UNBOUNDED_ARRAY = "unbounded_array"  # 无界数组类型
    SEQUENCE = "sequence"  # 序列类型
    BOUNDED_SEQUENCE = "bounded_sequence"  # 有界序列类型
    UNBOUNDED_SEQUENCE = "unbounded_sequence"  # 无界序列类型
    OBJECT = "object"  # 对象/映射类型

    # 扩展类型
    DATETIME = "datetime"  # 日期时间类型
    TIME = "time"  # 时间类型
    DURATION = "duration"  # 持续时间类型
    BYTES = "bytes"  # 字节数据类型
    DECIMAL = "decimal"  # 精确小数类型

    # 特殊类型
    UNKNOWN = "unknown"  # 未知类型
    ANY = "any"  # 任意类型

    @property
    def IS_ARRAY(self) -> bool:
        """判断该类型是否为数组/序列类型"""
        array_like = {
            StandardType.ARRAY,
            StandardType.BOUNDED_ARRAY,
            StandardType.UNBOUNDED_ARRAY,
            StandardType.SEQUENCE,
            StandardType.BOUNDED_SEQUENCE,
            StandardType.UNBOUNDED_SEQUENCE,
        }
        return self in array_like


class TypeConverter:
    """类型转换器，负责不同数据源类型之间的转换和标准化"""

    # Python基础类型到标准类型的映射
    PYTHON_TO_STANDARD = {
        str: StandardType.STRING,
        int: StandardType.INTEGER,  # 保持向后兼容的通用整数
        float: StandardType.FLOAT,  # 保持向后兼容的通用浮点
        bool: StandardType.BOOLEAN,
        type(None): StandardType.NULL,
        list: StandardType.ARRAY,
        tuple: StandardType.ARRAY,
        dict: StandardType.OBJECT,
        datetime: StandardType.DATETIME,
        bytes: StandardType.BYTES,
        bytearray: StandardType.BYTES,
        Decimal: StandardType.DECIMAL,
    }

    # 标准类型到Python类型的映射
    STANDARD_TO_PYTHON = {
        # 字符串类型
        StandardType.STRING: str,
        StandardType.WSTRING: str,
        StandardType.CHAR: str,
        StandardType.WCHAR: str,
        # 整数类型（都映射到int，Python会自动处理范围）
        StandardType.INT8: int,
        StandardType.UINT8: int,
        StandardType.INT16: int,
        StandardType.UINT16: int,
        StandardType.INT32: int,
        StandardType.UINT32: int,
        StandardType.INT64: int,
        StandardType.UINT64: int,
        StandardType.INTEGER: int,
        StandardType.BYTE: int,
        StandardType.OCTET: int,
        # 浮点类型
        StandardType.FLOAT32: float,
        StandardType.FLOAT64: float,
        StandardType.DOUBLE: float,
        StandardType.FLOAT: float,
        # 布尔类型
        StandardType.BOOLEAN: bool,
        StandardType.BOOL: bool,
        # 空值类型
        StandardType.NULL: type(None),
        # 容器类型
        StandardType.ARRAY: list,
        StandardType.BOUNDED_ARRAY: list,
        StandardType.UNBOUNDED_ARRAY: list,
        StandardType.SEQUENCE: list,
        StandardType.BOUNDED_SEQUENCE: list,
        StandardType.UNBOUNDED_SEQUENCE: list,
        StandardType.OBJECT: dict,
        # 扩展类型
        StandardType.DATETIME: datetime,
        StandardType.TIME: datetime,
        StandardType.DURATION: float,  # 持续时间用秒表示
        StandardType.BYTES: bytes,
        StandardType.DECIMAL: Decimal,
        # 特殊类型
        StandardType.UNKNOWN: object,
        StandardType.ANY: object,
    }

    # ROS2类型到标准类型的映射（保留原始类型精度）
    ROS2_TO_STANDARD = {
        # 字符串类型（保留具体类型）
        "string": StandardType.STRING,
        "wstring": StandardType.WSTRING,
        "char": StandardType.CHAR,
        "wchar": StandardType.WCHAR,
        # 整数类型（保留精度信息）
        "int8": StandardType.INT8,
        "uint8": StandardType.UINT8,
        "int16": StandardType.INT16,
        "short": StandardType.INT16,  # to check
        "uint16": StandardType.UINT16,
        "unsigned short": StandardType.UINT16,  # to check
        "int32": StandardType.INT32,
        "uint32": StandardType.UINT32,
        "int64": StandardType.INT64,
        "long": StandardType.INT64,  # to check
        "long long": StandardType.INT64,  # to check
        "uint64": StandardType.UINT64,
        "unsigned long": StandardType.UINT64,  # to check
        "unsigned long long": StandardType.UINT64,  # to check
        "byte": StandardType.BYTE,
        "octet": StandardType.OCTET,
        # 浮点类型（保留精度信息）
        "float32": StandardType.FLOAT32,
        "float64": StandardType.FLOAT64,
        "double": StandardType.DOUBLE,
        "long double": StandardType.DOUBLE,
        "float": StandardType.FLOAT32,  # 默认为32位
        # 布尔类型
        "bool": StandardType.BOOL,
        "boolean": StandardType.BOOLEAN,
        # 时间和持续时间（更精确的类型映射）
        "time": StandardType.TIME,
        "duration": StandardType.DURATION,
        # 向后兼容的通用映射（当需要时可以回退到这些）
        "generic_int": StandardType.INTEGER,
        "generic_float": StandardType.FLOAT,
        "generic_bool": StandardType.BOOLEAN,
        "generic_string": StandardType.STRING,
    }

    # JSON Schema类型到标准类型的映射
    JSON_SCHEMA_TO_STANDARD = {
        "string": StandardType.STRING,
        "integer": StandardType.INTEGER,
        "number": StandardType.FLOAT,
        "boolean": StandardType.BOOLEAN,
        "null": StandardType.NULL,
        "array": StandardType.ARRAY,
        "object": StandardType.OBJECT,
    }

    # 标准类型到Python类型的映射
    STANDARD_TO_JSON_SCHEMA = {
        # 字符串类型
        StandardType.STRING: "string",
        StandardType.WSTRING: "string",
        StandardType.CHAR: "string",
        StandardType.WCHAR: "string",
        # 整数类型（都映射到int，Python会自动处理范围）
        StandardType.INT8: "integer",
        StandardType.UINT8: "integer",
        StandardType.INT16: "integer",
        StandardType.UINT16: "integer",
        StandardType.INT32: "integer",
        StandardType.UINT32: "integer",
        StandardType.INT64: "integer",
        StandardType.UINT64: "integer",
        StandardType.INTEGER: "integer",
        StandardType.BYTE: "integer",
        StandardType.OCTET: "integer",
        # 浮点类型
        StandardType.FLOAT32: "number",
        StandardType.FLOAT64: "number",
        StandardType.DOUBLE: "number",
        StandardType.FLOAT: "number",
        # 布尔类型
        StandardType.BOOLEAN: "boolean",
        StandardType.BOOL: "boolean",
        # 空值类型
        StandardType.NULL: "null",
        # 容器类型
        StandardType.ARRAY: "array",
        StandardType.BOUNDED_ARRAY: "array",
        StandardType.UNBOUNDED_ARRAY: "array",
        StandardType.SEQUENCE: "array",
        StandardType.BOUNDED_SEQUENCE: "array",
        StandardType.UNBOUNDED_SEQUENCE: "array",
        StandardType.OBJECT: "object",
        # 扩展类型
        StandardType.DATETIME: "string",  # 在JSON Schema中日期时间通常表示为字符串
        StandardType.TIME: "string",
        StandardType.DURATION: "number",
        StandardType.BYTES: "string",  # 字节数据在JSON Schema中通常表示为base64字符串
        StandardType.DECIMAL: "number",
        # 特殊类型
        StandardType.UNKNOWN: "string",
        StandardType.ANY: "string",
    }

    # Array typecode到标准类型的映射（更精确的类型保留）
    ARRAY_TYPECODE_TO_STANDARD = {
        "b": StandardType.INT8,  # signed char
        "B": StandardType.UINT8,  # unsigned char
        "h": StandardType.INT16,  # signed short
        "H": StandardType.UINT16,  # unsigned short
        "i": StandardType.INT32,  # signed int
        "I": StandardType.UINT32,  # unsigned int
        "l": StandardType.INT64,  # signed long
        "L": StandardType.UINT64,  # unsigned long
        "f": StandardType.FLOAT32,  # float
        "d": StandardType.FLOAT64,  # double
    }

    # Array typecode到Python类型的映射
    ARRAY_TYPECODE_TO_PYTHON = {
        "b": int,  # signed char
        "B": int,  # unsigned char
        "h": int,  # signed short
        "H": int,  # unsigned short
        "i": int,  # signed int
        "I": int,  # unsigned int
        "l": int,  # signed long
        "L": int,  # unsigned long
        "f": float,  # float
        "d": float,  # double
    }

    """Python Type"""

    @classmethod
    def python_type_to_standard(cls, python_type: Type) -> StandardType:
        """将Python类型转换为标准类型"""
        # 处理泛型类型
        origin = get_origin(python_type)
        if origin is not None:
            if origin in (list, tuple):
                return StandardType.ARRAY
            elif origin is dict:
                return StandardType.OBJECT
            elif origin in (Union, type(Union[int, None])):
                # 处理Optional类型和Union类型
                args = get_args(python_type)
                non_none_types = [arg for arg in args if arg != type(None)]
                if len(non_none_types) == 1:
                    return cls.python_type_to_standard(non_none_types[0])
                return StandardType.ANY

        # 处理基础类型
        return cls.PYTHON_TO_STANDARD.get(python_type, StandardType.UNKNOWN)

    @classmethod
    def standard_to_python_type(cls, standard_type: StandardType) -> Type:
        """将标准类型转换为Python类型"""
        return cls.STANDARD_TO_PYTHON.get(standard_type, object)

    """ROS2"""

    @classmethod
    def ros2_type_str_to_standard(cls, ros2_type_str: str) -> StandardType:
        """将ROS2类型字符串转换为标准类型"""
        if "[" in ros2_type_str and "]" in ros2_type_str:
            return StandardType.ARRAY
        base_type = ros2_type_str.split("/")[-1].lower()
        return cls.ROS2_TO_STANDARD.get(base_type, StandardType.UNKNOWN)

    @classmethod
    def rosidl_definition_to_standard(cls, definition_type: Any) -> StandardType:
        from rosidl_parser.definition import (  # type: ignore
            Array,
            BasicType,
            BoundedSequence,
            BoundedString,
            BoundedWString,
            NamedType,
            NamespacedType,
            UnboundedSequence,
            UnboundedString,
            UnboundedWString,
        )

        # 基础类型转换（保留原始类型精度）
        if isinstance(definition_type, BasicType):
            type_name = definition_type.typename.lower()
            return cls.ros2_type_str_to_standard(type_name)
        # 字符串类型（区分普通字符串和宽字符串）
        elif isinstance(definition_type, (UnboundedString, BoundedString)):
            return StandardType.STRING
        elif isinstance(definition_type, (UnboundedWString, BoundedWString)):
            return StandardType.WSTRING
        # 数组和序列类型（更精确的类型区分）
        elif isinstance(definition_type, Array):
            return StandardType.BOUNDED_ARRAY
        elif isinstance(definition_type, UnboundedSequence):
            return StandardType.UNBOUNDED_SEQUENCE
        elif isinstance(definition_type, BoundedSequence):
            return StandardType.BOUNDED_SEQUENCE
        # 命名类型和命名空间类型统一为OBJECT
        elif isinstance(definition_type, (NamedType, NamespacedType)):
            return StandardType.OBJECT
        # 未知类型
        else:
            return StandardType.UNKNOWN

    @classmethod
    def array_typecode_to_standard(cls, typecode: str) -> StandardType:
        """将array.array的typecode转换为标准类型"""
        return cls.ARRAY_TYPECODE_TO_STANDARD.get(typecode, StandardType.UNKNOWN)

    """JSON Schema"""

    @classmethod
    def json_schema_type_to_standard(cls, json_type: str) -> StandardType:
        """将JSON Schema类型转换为标准类型"""
        return cls.JSON_SCHEMA_TO_STANDARD.get(json_type, StandardType.UNKNOWN)

    @classmethod
    def standard_type_to_json_schema_type(cls, standard_type: StandardType) -> str:
        """将StandardType转换为JSON Schema类型字符串"""
        return cls.STANDARD_TO_JSON_SCHEMA.get(standard_type, "string")

    """值转换"""

    @classmethod
    def convert_to_python_value_with_standard_type(cls, value: Any, target_standard_type: StandardType) -> Any:
        """将值转换为指定的标准类型对应的Python值"""
        if value is None:
            return None if target_standard_type == StandardType.NULL else None
        target_python_type = cls.standard_to_python_type(target_standard_type)
        if target_python_type != object and type(value) == target_python_type:
            # object交由target_standard_type为OBJECT的分支处理，同样返回原值
            return value
        if target_standard_type == StandardType.ARRAY:
            if isinstance(value, (list, tuple)):
                return list(value)
            elif hasattr(value, "typecode"):  # array.array
                return list(value)
            elif isinstance(value, str):
                return list(value)  # 字符串转为字符数组
            else:
                return [value]  # 单个值包装为数组
        elif target_standard_type == StandardType.OBJECT:
            return value
        elif target_standard_type == StandardType.DATETIME:
            if isinstance(value, datetime):
                return value
            elif isinstance(value, (int, float)):
                return datetime.fromtimestamp(value)
            elif isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            else:
                return datetime.now()
        elif target_standard_type == StandardType.BYTES:
            if isinstance(value, bytes):
                return value
            elif isinstance(value, str):
                return value.encode("utf-8")
            elif isinstance(value, (list, tuple)):
                return bytes(value)
            else:
                return str(value).encode("utf-8")
        else:
            # 基础类型转换
            return target_python_type(value)
