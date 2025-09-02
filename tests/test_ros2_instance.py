import array
import os
import sys

import pytest

from msgcenterpy import TypeConverter

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ROS2 dependency check
try:
    from geometry_msgs.msg import Point, Pose
    from std_msgs.msg import Float64MultiArray, String

    # Only import ROS2MessageInstance when ROS2 message packages are available
    from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False


from msgcenterpy.core.types import MessageType


class TestROS2MessageInstance:
    """ROS2MessageInstance test class"""

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_basic_creation_string_message(self):
        """Test basic String message creation"""
        # Create String message
        string_msg = String()
        string_msg.data = "Hello ROS2"

        # Create ROS2MessageInstance
        ros2_inst = ROS2MessageInstance(string_msg)

        assert ros2_inst.message_type == MessageType.ROS2
        assert ros2_inst.inner_data is string_msg
        assert ros2_inst.ros_msg_cls == String
        assert ros2_inst.ros_msg_cls_namespace == "std_msgs/msg/String"

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_basic_creation_float_array(self):
        """Test Float64MultiArray message creation"""
        # Create Float64MultiArray message
        array_msg = Float64MultiArray()
        array_msg.data = [1.1, 2.2, 3.3, 4.4, 5.5]

        # Create ROS2MessageInstance
        ros2_inst = ROS2MessageInstance(array_msg)

        assert ros2_inst.message_type == MessageType.ROS2
        assert ros2_inst.inner_data is array_msg
        assert ros2_inst.ros_msg_cls == Float64MultiArray

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_simple_field_assignment(self):
        """Test simple field assignment - based on __main__ test1"""
        # Create String message
        string_msg = String()
        ros2_inst = ROS2MessageInstance(string_msg)

        # Initial state check
        assert string_msg.data == ""

        # Test field assignment
        ros2_inst.data = "test_value"  # Assignment through field accessor
        assert string_msg.data == "test_value"
        assert ros2_inst.inner_data.data == "test_value"

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_nested_field_assignment(self):
        """测试嵌套字段赋值 - 基于 __main__ 测试2,3"""
        # Create Pose message
        pose_msg = Pose()
        ros2_inst = ROS2MessageInstance(pose_msg)

        # 测试嵌套字段赋值
        ros2_inst.position.x = 1.5
        ros2_inst.position.y = 2.5
        ros2_inst.position.z = 3.5

        assert pose_msg.position.x == 1.5
        assert pose_msg.position.y == 2.5
        assert pose_msg.position.z == 3.5

        # 测试整个对象赋值
        new_position = Point(x=10.0, y=20.0, z=30.0)
        ros2_inst.position = new_position

        assert pose_msg.position.x == 10.0
        assert pose_msg.position.y == 20.0
        assert pose_msg.position.z == 30.0

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_export_to_envelope(self):
        """测试导出信封功能 - 基于 __main__ 测试6"""
        # Create and setup String message
        string_msg = String()
        string_msg.data = "test_envelope_data"
        ros2_inst = ROS2MessageInstance(string_msg)

        # 导出信封
        envelope = ros2_inst.export_to_envelope()

        # 验证信封结构
        assert "content" in envelope
        assert "metadata" in envelope
        assert envelope["content"]["data"] == "test_envelope_data"

        # 验证元数据
        metadata = envelope["metadata"]
        assert metadata["current_format"] == "ros2"
        assert "properties" in metadata

        properties = metadata["properties"]
        assert "ros_msg_cls_namespace" in properties
        assert "ros_msg_cls_path" in properties

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_get_python_dict(self):
        """测试获取 Python 字典"""
        # Create Float64MultiArray message
        array_msg = Float64MultiArray()
        array_msg.data = [1.0, 2.0, 3.0]
        ros2_inst = ROS2MessageInstance(array_msg)

        # 获取 Python 字典
        python_dict = ros2_inst.get_python_dict()

        assert isinstance(python_dict, dict)
        assert "data" in python_dict
        assert python_dict["data"] == [1.0, 2.0, 3.0]

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_set_python_dict(self):
        """测试设置 Python 字典"""
        # Create String message
        string_msg = String()
        ros2_inst = ROS2MessageInstance(string_msg)

        # 设置字典数据
        new_data = {"data": "updated_value"}
        result = ros2_inst.set_python_dict(new_data)

        assert result is True
        assert string_msg.data == "updated_value"

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_field_type_info_extraction(self):
        """测试字段类型信息提取"""
        # Create Float64MultiArray message
        array_msg = Float64MultiArray()
        array_msg.data = [1.0, 2.0, 3.0]
        ros2_inst = ROS2MessageInstance(array_msg)

        # 获取字段类型信息
        type_info = ros2_inst.fields.get_sub_type_info("data")

        assert type_info is not None
        assert type_info.field_name == "data"
        assert type_info.is_array is True
        assert type_info.python_type == array.array
        assert type_info.python_value_from_standard_type == [1.0, 2.0, 3.0]

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_obtain_ros_cls_from_string(self):
        """测试从字符串获取 ROS 类"""
        # 测试 namespace 格式
        ros_cls_ns = ROS2MessageInstance.obtain_ros_cls_from_str("std_msgs/msg/String")
        assert ros_cls_ns == String

        # 测试模块路径格式
        ros_cls_path = ROS2MessageInstance.obtain_ros_cls_from_str("std_msgs.msg._string.String")
        assert ros_cls_path == String

        # 测试直接传入类
        ros_cls_direct = ROS2MessageInstance.obtain_ros_cls_from_str(String)
        assert ros_cls_direct == String

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_ros_msg_cls_properties(self):
        """测试 ROS 消息类属性"""
        string_msg = String()
        ros2_inst = ROS2MessageInstance(string_msg)

        # 测试类路径属性
        cls_path = ros2_inst.ros_msg_cls_path
        assert "std_msgs.msg" in cls_path
        assert "String" in cls_path

        # 测试命名空间属性
        namespace = ros2_inst.ros_msg_cls_namespace
        assert namespace == "std_msgs/msg/String"

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_import_from_envelope(self):
        """测试从信封导入"""
        # Create original message
        original_msg = String()
        original_msg.data = "envelope_test"
        original_inst = ROS2MessageInstance(original_msg)

        # 导出信封
        envelope = original_inst.export_to_envelope()

        # 从信封导入新实例
        new_inst = ROS2MessageInstance.import_from_envelope(envelope)

        assert isinstance(new_inst, ROS2MessageInstance)
        assert new_inst.inner_data.data == "envelope_test"
        assert new_inst.ros_msg_cls == String


class TestROS2MessageInstanceJSONSchema:
    """ROS2MessageInstance JSON Schema 生成测试"""

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_get_json_schema_string_message(self):
        """测试 String 消息的 JSON Schema 生成"""
        string_msg = String()
        string_msg.data = "test_schema"
        ros2_inst = ROS2MessageInstance(string_msg)

        # 生成 JSON Schema
        schema = ros2_inst.get_json_schema()

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "data" in schema["properties"]
        assert schema["properties"]["data"]["type"] == "string"
        assert schema["title"] == "ROS2MessageInstance Schema"

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_get_json_schema_float_array(self):
        """测试 Float64MultiArray 的 JSON Schema 生成"""
        array_msg = Float64MultiArray()
        array_msg.data = [1.1, 2.2, 3.3]
        ros2_inst = ROS2MessageInstance(array_msg)

        # 生成 JSON Schema
        schema = ros2_inst.get_json_schema()

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "data" in schema["properties"]

        # 检查数组类型
        data_prop = schema["properties"]["data"]
        assert data_prop["type"] == "array"
        assert "items" in data_prop
        assert data_prop["items"]["type"] == "number"

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_get_json_schema_pose_message(self):
        """测试复杂 Pose 消息的 JSON Schema 生成"""
        pose_msg = Pose()
        pose_msg.position.x = 1.0
        pose_msg.position.y = 2.0
        pose_msg.position.z = 3.0
        ros2_inst = ROS2MessageInstance(pose_msg)

        # 生成 JSON Schema
        schema = ros2_inst.get_json_schema()

        assert schema["type"] == "object"
        assert "properties" in schema

        # 检查嵌套对象
        properties = schema["properties"]
        assert "position" in properties
        assert "orientation" in properties

        # 验证对象类型
        position_prop = properties["position"]
        assert position_prop["type"] == "object"

    @pytest.mark.skipif(not HAS_ROS2, reason="ROS2 dependencies not available")
    def test_json_schema_constraint_extraction(self):
        """测试约束条件提取"""
        array_msg = Float64MultiArray()
        array_msg.data = [1.0, 2.0, 3.0, 4.0, 5.0]
        ros2_inst = ROS2MessageInstance(array_msg)

        # 获取字段类型信息检查约束
        type_info = ros2_inst.fields.get_sub_type_info("data")

        assert type_info is not None
        assert type_info.is_array is True

        # 生成 Schema 并检查约束是否转换
        schema = ros2_inst.get_json_schema()
        data_prop = schema["properties"]["data"]
        assert data_prop["type"] == "array"


# 运行测试的便捷函数
def run_ros2_tests():
    """运行 ROS2 相关测试"""
    if not HAS_ROS2:
        print("❌ ROS2 dependencies not available, skipping tests")
        return False

    import subprocess

    result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_ros2_instance.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    # 直接运行测试
    run_ros2_tests()
