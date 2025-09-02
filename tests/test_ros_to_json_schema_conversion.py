import os
import sys

import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 依赖检查
try:
    from geometry_msgs.msg import Point, Pose, Vector3
    from std_msgs.msg import Bool, Float64MultiArray, Int32, String

    # 只有在 ROS2 消息包可用时才导入 ROS2MessageInstance
    from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False


import jsonschema

from msgcenterpy.core.types import MessageType
from msgcenterpy.instances.json_schema_instance import JSONSchemaMessageInstance


class TestROS2ToJSONSchemaConversion:
    """ROS2 转 JSON Schema 转换测试"""

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_string_message_to_json_schema(self):
        """测试 String 消息转 JSON Schema"""
        # 创建 ROS2 String 消息
        string_msg = String()
        string_msg.data = "Hello JSON Schema"
        ros2_inst = ROS2MessageInstance(string_msg)

        # 生成 JSON Schema
        schema = ros2_inst.get_json_schema()

        # 验证 Schema 结构
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "data" in schema["properties"]
        assert schema["properties"]["data"]["type"] == "string"
        assert schema["title"] == "ROS2MessageInstance Schema"
        assert "ros2" in schema["description"]

        # 验证与原始数据的一致性
        ros2_dict = ros2_inst.get_python_dict()
        assert "data" in ros2_dict
        assert ros2_dict["data"] == "Hello JSON Schema"

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_float_array_to_json_schema(self):
        """测试 Float64MultiArray 转 JSON Schema"""
        # 创建 Float64MultiArray 消息
        array_msg = Float64MultiArray()
        array_msg.data = [1.1, 2.2, 3.3, 4.4, 5.5]
        ros2_inst = ROS2MessageInstance(array_msg)

        # 生成 JSON Schema
        schema = ros2_inst.get_json_schema()

        # 验证数组字段的 Schema
        assert "data" in schema["properties"]
        data_prop = schema["properties"]["data"]
        assert data_prop["type"] == "array"
        assert "items" in data_prop
        assert data_prop["items"]["type"] == "number"

        # 验证约束条件
        assert "minItems" in data_prop or "maxItems" in data_prop or data_prop["type"] == "array"

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_pose_message_to_json_schema(self):
        """测试复杂 Pose 消息转 JSON Schema"""
        # 创建 Pose 消息
        pose_msg = Pose()
        pose_msg.position.x = 1.0
        pose_msg.position.y = 2.0
        pose_msg.position.z = 3.0
        pose_msg.orientation.w = 1.0
        ros2_inst = ROS2MessageInstance(pose_msg)

        # 生成 JSON Schema
        schema = ros2_inst.get_json_schema()

        # 验证嵌套对象结构
        properties = schema["properties"]
        assert "position" in properties
        assert "orientation" in properties

        # 验证对象类型
        position_prop = properties["position"]
        assert position_prop["type"] == "object"

        orientation_prop = properties["orientation"]
        assert orientation_prop["type"] == "object"


class TestROS2ToJSONSchemaInstanceConversion:
    """ROS2 转 JSONSchemaMessageInstance 转换测试"""

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_ros2_to_json_schema_instance_string(self):
        """测试 ROS2 String 转 JSONSchemaMessageInstance"""
        # 创建 ROS2 实例
        string_msg = String()
        string_msg.data = "Test conversion"
        ros2_inst = ROS2MessageInstance(string_msg)

        # 转换为 JSONSchemaMessageInstance
        json_schema_inst = ros2_inst.to_json_schema()

        # 验证转换结果
        assert isinstance(json_schema_inst, JSONSchemaMessageInstance)
        assert json_schema_inst.message_type == MessageType.JSON_SCHEMA

        # 验证数据一致性
        original_data = ros2_inst.get_python_dict()
        converted_data = json_schema_inst.get_python_dict()
        assert original_data == converted_data

        # 验证 Schema 存在
        schema = json_schema_inst.json_schema
        assert schema is not None
        assert schema["type"] == "object"
        assert "properties" in schema

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_ros2_to_json_schema_instance_array(self):
        """测试 ROS2 数组转 JSONSchemaMessageInstance"""
        # 创建 ROS2 数组实例
        array_msg = Float64MultiArray()
        array_msg.data = [10.5, 20.3, 30.7]
        ros2_inst = ROS2MessageInstance(array_msg)

        # 转换为 JSONSchemaMessageInstance
        json_schema_inst = ros2_inst.to_json_schema()

        # 验证转换结果
        assert isinstance(json_schema_inst, JSONSchemaMessageInstance)

        # 验证数据一致性
        original_data = ros2_inst.get_python_dict()
        converted_data = json_schema_inst.get_python_dict()
        assert original_data == converted_data
        assert converted_data["data"] == [10.5, 20.3, 30.7]

        # 验证 Schema 的数组类型
        schema = json_schema_inst.json_schema
        if "data" in schema["properties"]:
            data_prop = schema["properties"]["data"]
            assert data_prop["type"] == "array"

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_ros2_to_json_schema_instance_pose(self):
        """测试 ROS2 Pose 转 JSONSchemaMessageInstance"""
        # 创建复杂的 Pose 消息
        pose_msg = Pose()
        pose_msg.position.x = 5.0
        pose_msg.position.y = 10.0
        pose_msg.position.z = 15.0
        pose_msg.orientation.x = 0.0
        pose_msg.orientation.y = 0.0
        pose_msg.orientation.z = 0.0
        pose_msg.orientation.w = 1.0
        ros2_inst = ROS2MessageInstance(pose_msg)

        # 转换为 JSONSchemaMessageInstance
        json_schema_inst = ros2_inst.to_json_schema()

        # 验证转换结果
        assert isinstance(json_schema_inst, JSONSchemaMessageInstance)

        # 验证嵌套数据一致性
        original_data = ros2_inst.get_python_dict()
        converted_data = json_schema_inst.get_python_dict()
        assert original_data == converted_data

        # 验证嵌套结构
        assert "position" in converted_data
        assert "orientation" in converted_data
        assert converted_data["position"]["x"] == 5.0
        assert converted_data["position"]["y"] == 10.0
        assert converted_data["position"]["z"] == 15.0


class TestConversionConsistency:
    """转换一致性测试"""

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_schema_data_consistency(self):
        """测试 Schema 与数据的一致性"""
        # 创建多种类型的数据
        test_cases = []

        # String 消息
        string_msg = String()
        string_msg.data = "consistency_test"
        test_cases.append(("String", ROS2MessageInstance(string_msg)))

        # Float64MultiArray 消息
        array_msg = Float64MultiArray()
        array_msg.data = [1.0, 2.0, 3.0]
        test_cases.append(("Float64MultiArray", ROS2MessageInstance(array_msg)))

        for test_name, ros2_inst in test_cases:
            # 生成 Schema
            schema = ros2_inst.get_json_schema()
            original_data = ros2_inst.get_python_dict()

            # 验证 Schema 属性与数据字段一致
            schema_props = set(schema["properties"].keys())
            data_keys = set(original_data.keys())

            assert schema_props == data_keys, f"{test_name}: Schema properties and data keys don't match"

            # 验证每个字段的类型一致性
            for field_name, field_value in original_data.items():
                if field_name in schema["properties"]:
                    prop_schema = schema["properties"][field_name]

                    # 基本类型检查
                    if isinstance(field_value, str):
                        assert prop_schema["type"] == "string", f"{test_name}.{field_name}: Type mismatch"
                    elif isinstance(field_value, bool):
                        assert prop_schema["type"] == "boolean", f"{test_name}.{field_name}: Type mismatch"
                    elif isinstance(field_value, int):
                        assert prop_schema["type"] == "integer", f"{test_name}.{field_name}: Type mismatch"
                    elif isinstance(field_value, float):
                        assert prop_schema["type"] == "number", f"{test_name}.{field_name}: Type mismatch"
                    elif isinstance(field_value, list):
                        assert prop_schema["type"] == "array", f"{test_name}.{field_name}: Type mismatch"
                    elif isinstance(field_value, dict):
                        assert prop_schema["type"] == "object", f"{test_name}.{field_name}: Type mismatch"

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_conversion_roundtrip_data(self):
        """测试转换往返的数据一致性"""
        # 创建原始 ROS2 消息
        string_msg = String()
        string_msg.data = "roundtrip_test"
        original_ros2_inst = ROS2MessageInstance(string_msg)
        original_data = original_ros2_inst.get_python_dict()

        # ROS2 -> JSONSchema
        json_schema_inst = original_ros2_inst.to_json_schema()
        converted_data = json_schema_inst.get_python_dict()

        # 验证数据在转换过程中保持一致
        assert original_data == converted_data

        # 验证 Schema 的有效性
        schema = json_schema_inst.json_schema
        assert schema is not None

        # 使用 jsonschema 库验证数据符合生成的 Schema
        try:
            jsonschema.validate(converted_data, schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"Generated data doesn't match generated schema: {e}")

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_multiple_message_types_conversion(self):
        """测试多种消息类型的转换"""
        test_messages = []

        # String
        string_msg = String()
        string_msg.data = "multi_test_string"
        test_messages.append(("String", string_msg))

        # Float64MultiArray
        array_msg = Float64MultiArray()
        array_msg.data = [1.5, 2.5, 3.5]
        test_messages.append(("Float64MultiArray", array_msg))

        # Point
        point_msg = Point()
        point_msg.x = 1.0
        point_msg.y = 2.0
        point_msg.z = 3.0
        test_messages.append(("Point", point_msg))

        for msg_type_name, msg in test_messages:
            # 创建 ROS2 实例
            ros2_inst = ROS2MessageInstance(msg)

            # 转换为 JSONSchema 实例
            json_schema_inst = ros2_inst.to_json_schema()

            # 验证转换成功
            assert isinstance(json_schema_inst, JSONSchemaMessageInstance)
            assert json_schema_inst.message_type == MessageType.JSON_SCHEMA

            # 验证数据一致性
            original_data = ros2_inst.get_python_dict()
            converted_data = json_schema_inst.get_python_dict()
            assert original_data == converted_data, f"{msg_type_name}: Data inconsistency after conversion"

            # 验证 Schema 生成
            schema = json_schema_inst.json_schema
            assert schema is not None
            assert schema["type"] == "object"
            assert len(schema["properties"]) > 0, f"{msg_type_name}: No properties in generated schema"


class TestConversionErrorHandling:
    """转换错误处理测试"""

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_empty_message_conversion(self):
        """测试空消息的转换"""
        # 创建空的 String 消息
        empty_string = String()
        ros2_inst = ROS2MessageInstance(empty_string)

        # 转换应该成功，即使数据为空
        json_schema_inst = ros2_inst.to_json_schema()

        assert isinstance(json_schema_inst, JSONSchemaMessageInstance)

        # 验证 Schema 仍然有效
        schema = json_schema_inst.json_schema
        assert schema["type"] == "object"
        assert "properties" in schema

    @pytest.mark.skipif(not HAS_ROS2, reason="Missing dependencies")
    def test_large_data_conversion(self):
        """测试大数据量的转换"""
        # 创建包含大量数据的数组消息
        large_array = Float64MultiArray()
        large_array.data = [float(i) for i in range(1000)]  # 1000 个浮点数
        ros2_inst = ROS2MessageInstance(large_array)

        # 转换应该能处理大数据量
        json_schema_inst = ros2_inst.to_json_schema()

        assert isinstance(json_schema_inst, JSONSchemaMessageInstance)

        # 验证数据完整性
        original_data = ros2_inst.get_python_dict()
        converted_data = json_schema_inst.get_python_dict()
        assert len(original_data["data"]) == 1000
        assert len(converted_data["data"]) == 1000
        assert original_data == converted_data


# 运行测试的便捷函数
def run_conversion_tests():
    """运行转换测试"""
    if not HAS_ROS2:
        print("❌ Required dependencies not available, skipping tests")
        print(f"  ROS2: {HAS_ROS2}")
        return False

    import subprocess

    result = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "tests/test_ros_to_json_schema_conversion.py",
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
    run_conversion_tests()
