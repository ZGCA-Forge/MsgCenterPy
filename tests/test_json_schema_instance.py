import os
import sys

import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# JSON Schema 依赖检查

from msgcenterpy.core.type_info import ConstraintType
from msgcenterpy.core.types import MessageType
from msgcenterpy.instances.json_schema_instance import JSONSchemaMessageInstance


class TestJSONSchemaMessageInstance:
    """JSONSchemaMessageInstance 基本功能测试"""

    @pytest.fixture
    def simple_schema(self):
        """简单的 JSON Schema 示例"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
                "active": {"type": "boolean"},
            },
            "required": ["name"],
        }

    @pytest.fixture
    def complex_schema(self):
        """复杂的 JSON Schema 示例"""
        return {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "profile": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string", "format": "email"},
                                "phone": {
                                    "type": "string",
                                    "pattern": "^\\+?[1-9]\\d{1,14}$",
                                },
                            },
                        },
                    },
                    "required": ["id"],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 10,
                },
                "scores": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0, "maximum": 100},
                },
                "metadata": {"type": "object", "additionalProperties": True},
            },
            "required": ["user", "tags"],
        }

    @pytest.fixture
    def simple_data(self):
        """匹配简单 schema 的数据"""
        return {"name": "John Doe", "age": 30, "active": True}

    @pytest.fixture
    def complex_data(self):
        """匹配复杂 schema 的数据"""
        return {
            "user": {
                "id": "user_123",
                "profile": {"email": "john@example.com", "phone": "+1234567890"},
            },
            "tags": ["developer", "python", "testing"],
            "scores": [85.5, 92.0, 78.3],
            "metadata": {"created_at": "2024-01-01", "version": 1},
        }

    def test_basic_creation(self, simple_schema, simple_data):
        """测试基本创建功能"""
        instance = JSONSchemaMessageInstance(simple_data, simple_schema)

        assert instance.message_type == MessageType.JSON_SCHEMA
        assert instance.inner_data == simple_data
        assert instance.json_schema == simple_schema
        assert len(instance._validation_errors) == 0

    def test_data_validation_success(self, simple_schema, simple_data):
        """测试数据验证成功"""
        instance = JSONSchemaMessageInstance(simple_data, simple_schema)

        # 验证成功，没有错误
        assert len(instance._validation_errors) == 0

    def test_data_validation_failure(self, simple_schema):
        """测试数据验证失败"""
        invalid_data = {
            "age": -5,  # 违反 minimum 约束
            "active": "not_boolean",  # 类型错误
            # 缺少必需的 "name" 字段
        }

        instance = JSONSchemaMessageInstance(invalid_data, simple_schema)

        # 应该有验证错误
        assert len(instance._validation_errors) > 0

    def test_get_python_dict(self, simple_schema, simple_data):
        """测试获取 Python 字典"""
        instance = JSONSchemaMessageInstance(simple_data, simple_schema)

        result = instance.get_python_dict()

        assert isinstance(result, dict)
        assert result == simple_data
        assert result is not simple_data  # 应该是副本

    def test_set_python_dict(self, simple_schema, simple_data):
        """测试设置 Python 字典"""
        instance = JSONSchemaMessageInstance(simple_data, simple_schema)

        new_data = {"name": "Jane Smith", "age": 25}

        result = instance.set_python_dict(new_data)

        assert result is True
        assert instance.get_python_dict()["name"] == "Jane Smith"
        assert instance.get_python_dict()["age"] == 25

    def test_export_to_envelope(self, simple_schema, simple_data):
        """测试导出信封"""
        instance = JSONSchemaMessageInstance(simple_data, simple_schema)

        envelope = instance.export_to_envelope()

        assert "content" in envelope
        assert "metadata" in envelope
        assert envelope["content"] == simple_data

        metadata = envelope["metadata"]
        assert metadata["current_format"] == "json_schema"
        assert "properties" in metadata

    def test_import_from_envelope(self, simple_schema, simple_data):
        """测试从信封导入"""
        # 创建原始实例
        original = JSONSchemaMessageInstance(simple_data, simple_schema)
        envelope = original.export_to_envelope()

        # 从信封导入新实例
        new_instance = JSONSchemaMessageInstance.import_from_envelope(envelope)

        assert isinstance(new_instance, JSONSchemaMessageInstance)
        assert new_instance.get_python_dict() == simple_data
        assert new_instance.json_schema == simple_schema


class TestJSONSchemaFieldTypeInfo:
    """JSON Schema 字段类型信息测试"""

    @pytest.fixture
    def typed_schema(self):
        """包含各种类型的 schema"""
        return {
            "type": "object",
            "properties": {
                "string_field": {"type": "string", "minLength": 3, "maxLength": 50},
                "integer_field": {"type": "integer", "minimum": 0, "maximum": 100},
                "number_field": {"type": "number", "multipleOf": 0.5},
                "boolean_field": {"type": "boolean"},
                "array_field": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 5,
                },
                "object_field": {
                    "type": "object",
                    "properties": {"nested_string": {"type": "string"}},
                },
                "enum_field": {
                    "type": "string",
                    "enum": ["option1", "option2", "option3"],
                },
                "format_field": {"type": "string", "format": "email"},
            },
            "required": ["string_field", "integer_field"],
        }

    @pytest.fixture
    def typed_data(self):
        """匹配类型化 schema 的数据"""
        return {
            "string_field": "hello",
            "integer_field": 42,
            "number_field": 3.5,
            "boolean_field": True,
            "array_field": ["item1", "item2"],
            "object_field": {"nested_string": "nested_value"},
            "enum_field": "option1",
            "format_field": "test@example.com",
        }

    def test_string_field_type_info(self, typed_schema, typed_data):
        """测试字符串字段类型信息"""
        instance = JSONSchemaMessageInstance(typed_data, typed_schema)
        type_info = instance.fields.get_sub_type_info("string_field")

        assert type_info is not None
        assert type_info.field_name == "string_field"
        assert type_info.standard_type.value == "string"
        assert type_info.current_value == "hello"

        # 检查约束
        assert type_info.has_constraint(ConstraintType.MIN_LENGTH)
        assert type_info.get_constraint_value(ConstraintType.MIN_LENGTH) == 3
        assert type_info.has_constraint(ConstraintType.MAX_LENGTH)
        assert type_info.get_constraint_value(ConstraintType.MAX_LENGTH) == 50
        assert type_info.has_constraint(ConstraintType.REQUIRED)

    def test_integer_field_type_info(self, typed_schema, typed_data):
        """测试整数字段类型信息"""
        instance = JSONSchemaMessageInstance(typed_data, typed_schema)
        type_info = instance.fields.get_sub_type_info("integer_field")

        assert type_info is not None
        assert type_info.standard_type.value == "integer"
        assert type_info.current_value == 42

        # 检查数值约束
        assert type_info.has_constraint(ConstraintType.MIN_VALUE)
        assert type_info.get_constraint_value(ConstraintType.MIN_VALUE) == 0
        assert type_info.has_constraint(ConstraintType.MAX_VALUE)
        assert type_info.get_constraint_value(ConstraintType.MAX_VALUE) == 100
        assert type_info.has_constraint(ConstraintType.REQUIRED)

    def test_array_field_type_info(self, typed_schema, typed_data):
        """测试数组字段类型信息"""
        instance = JSONSchemaMessageInstance(typed_data, typed_schema)
        type_info = instance.fields.get_sub_type_info("array_field")

        assert type_info is not None
        assert type_info.is_array is True
        assert type_info.current_value == ["item1", "item2"]

        # 检查数组约束
        assert type_info.has_constraint(ConstraintType.MIN_ITEMS)
        assert type_info.get_constraint_value(ConstraintType.MIN_ITEMS) == 1
        assert type_info.has_constraint(ConstraintType.MAX_ITEMS)
        assert type_info.get_constraint_value(ConstraintType.MAX_ITEMS) == 5

        # 检查元素类型信息
        assert type_info.element_type_info is not None
        assert type_info.element_type_info.standard_type.value == "string"

    def test_object_field_type_info(self, typed_schema, typed_data):
        """测试对象字段类型信息"""
        instance = JSONSchemaMessageInstance(typed_data, typed_schema)
        type_info = instance.fields.get_sub_type_info("object_field")

        assert type_info is not None
        assert type_info.is_object is True
        assert type_info.current_value == {"nested_string": "nested_value"}

        # 检查对象字段定义
        assert len(type_info.object_fields) > 0
        assert "nested_string" in type_info.object_fields

        nested_field_info = type_info.object_fields["nested_string"]
        assert nested_field_info.standard_type.value == "string"

    def test_enum_field_type_info(self, typed_schema, typed_data):
        """测试枚举字段类型信息"""
        instance = JSONSchemaMessageInstance(typed_data, typed_schema)
        type_info = instance.fields.get_sub_type_info("enum_field")

        assert type_info is not None
        assert type_info.has_constraint(ConstraintType.ENUM_VALUES)
        enum_values = type_info.get_constraint_value(ConstraintType.ENUM_VALUES)
        assert enum_values == ["option1", "option2", "option3"]

    def test_format_field_type_info(self, typed_schema, typed_data):
        """测试格式字段类型信息"""
        instance = JSONSchemaMessageInstance(typed_data, typed_schema)
        type_info = instance.fields.get_sub_type_info("format_field")

        assert type_info is not None
        assert type_info.has_constraint(ConstraintType.FORMAT)
        format_value = type_info.get_constraint_value(ConstraintType.FORMAT)
        assert format_value == "email"


class TestJSONSchemaInstanceJSONSchema:
    """JSONSchemaMessageInstance 自身的 JSON Schema 生成测试"""

    def test_get_json_schema_simple(self):
        """测试简单数据的 JSON Schema 生成"""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "count": {"type": "integer"}},
        }
        data = {"name": "test", "count": 5}

        instance = JSONSchemaMessageInstance(data, schema)
        generated_schema = instance.get_json_schema()

        assert generated_schema["type"] == "object"
        assert "properties" in generated_schema
        assert "name" in generated_schema["properties"]
        assert "count" in generated_schema["properties"]
        assert generated_schema["title"] == "JSONSchemaMessageInstance Schema"

    def test_get_json_schema_with_constraints(self):
        """测试包含约束的 JSON Schema 生成"""
        schema = {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email", "minLength": 5},
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
                "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            },
            "required": ["email"],
        }
        data = {"email": "test@example.com", "age": 25, "tags": ["tag1", "tag2"]}

        instance = JSONSchemaMessageInstance(data, schema)
        generated_schema = instance.get_json_schema()

        # 检查约束是否保留在生成的 schema 中
        properties = generated_schema["properties"]

        # email 字段约束
        email_prop = properties["email"]
        assert email_prop["type"] == "string"

        # age 字段约束
        age_prop = properties["age"]
        assert age_prop["type"] == "integer"

        # tags 数组约束
        tags_prop = properties["tags"]
        assert tags_prop["type"] == "array"

    def test_get_json_schema_nested_objects(self):
        """测试嵌套对象的 JSON Schema 生成"""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "settings": {
                            "type": "object",
                            "properties": {"theme": {"type": "string"}},
                        },
                    },
                }
            },
        }
        data = {"user": {"id": "user123", "settings": {"theme": "dark"}}}

        instance = JSONSchemaMessageInstance(data, schema)
        generated_schema = instance.get_json_schema()

        assert "user" in generated_schema["properties"]
        user_prop = generated_schema["properties"]["user"]
        assert user_prop["type"] == "object"


class TestJSONSchemaValidation:
    """JSON Schema 验证功能测试"""

    def test_constraint_validation(self):
        """测试约束验证"""
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
                "name": {"type": "string", "minLength": 2, "maxLength": 50},
            },
            "required": ["name"],
        }

        # 有效数据
        valid_data = {"name": "John", "age": 30}
        valid_instance = JSONSchemaMessageInstance(valid_data, schema)
        assert len(valid_instance._validation_errors) == 0

        # 无效数据 - 年龄超出范围
        invalid_data1 = {"name": "John", "age": 200}
        invalid_instance1 = JSONSchemaMessageInstance(invalid_data1, schema)
        assert len(invalid_instance1._validation_errors) > 0

        # 无效数据 - 缺少必需字段
        invalid_data2 = {"age": 30}
        invalid_instance2 = JSONSchemaMessageInstance(invalid_data2, schema)
        assert len(invalid_instance2._validation_errors) > 0

    def test_type_validation(self):
        """测试类型验证"""
        schema = {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "active": {"type": "boolean"},
                "items": {"type": "array", "items": {"type": "string"}},
            },
        }

        # 类型正确的数据
        valid_data = {"count": 42, "active": True, "items": ["a", "b", "c"]}
        valid_instance = JSONSchemaMessageInstance(valid_data, schema)
        assert len(valid_instance._validation_errors) == 0

        # 类型错误的数据
        invalid_data = {
            "count": "not_integer",
            "active": "not_boolean",
            "items": "not_array",
        }
        invalid_instance = JSONSchemaMessageInstance(invalid_data, schema)
        assert len(invalid_instance._validation_errors) > 0


# 运行测试的便捷函数
def run_json_schema_tests():
    """运行 JSON Schema 相关测试"""

    import subprocess

    result = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "tests/test_json_schema_instance.py",
            "-v",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    # 直接运行测试
    run_json_schema_tests()
