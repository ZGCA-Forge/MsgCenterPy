# MsgCenterPy

<div align="center">

[![PyPI version](https://badge.fury.io/py/msgcenterpy.svg)](https://badge.fury.io/py/msgcenterpy)
[![Python versions](https://img.shields.io/pypi/pyversions/msgcenterpy.svg)](https://pypi.org/project/msgcenterpy/)
[![Build Status](https://github.com/ZGCA-Forge/MsgCenterPy/workflows/CI/badge.svg)](https://github.com/ZGCA-Forge/MsgCenterPy/actions)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-brightgreen)](https://zgca-forge.github.io/MsgCenterPy/)

[![GitHub stars](https://img.shields.io/github/stars/ZGCA-Forge/MsgCenterPy.svg?style=social&label=Star)](https://github.com/ZGCA-Forge/MsgCenterPy)
[![GitHub forks](https://img.shields.io/github/forks/ZGCA-Forge/MsgCenterPy.svg?style=social&label=Fork)](https://github.com/ZGCA-Forge/MsgCenterPy/fork)
[![GitHub issues](https://img.shields.io/github/issues/ZGCA-Forge/MsgCenterPy.svg)](https://github.com/ZGCA-Forge/MsgCenterPy/issues)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/ZGCA-Forge/MsgCenterPy/blob/main/LICENSE)

</div>

---

## 🚀 概述

MsgCenterPy 是一个基于统一实例管理器架构的多格式消息转换系统，支持 **ROS2**、**Pydantic**、**Dataclass**、**JSON**、**Dict**、**YAML** 和 **JSON Schema** 之间的无缝互转。

### 支持的格式

| 格式        | 读取   | 写入   | JSON Schema | 类型约束 |
| ----------- | ------ | ------ | ----------- | -------- |
| ROS2        | ✅     | ✅     | ✅          | ✅       |
| JSON Schema | ✅     | ✅     | ✅          | ✅       |
| Pydantic    | 开发中 | 开发中 | 开发中      | 开发中   |
| Dataclass   | 开发中 | 开发中 | 开发中      | 开发中   |
| JSON        | 开发中 | 开发中 | 开发中      | 开发中   |
| Dict        | 开发中 | 开发中 | 开发中      | 开发中   |
| YAML        | 开发中 | 开发中 | 开发中      | 开发中   |

## 📦 安装

### 基础安装

```bash
pip install msgcenterpy
```

### 包含可选依赖

```bash
# 安装 ROS2 支持
conda install

# 安装开发工具
pip install msgcenterpy[dev]

# 安装文档工具
pip install msgcenterpy[docs]

# 安装所有依赖
pip install msgcenterpy[all]
```

### 从源码安装

```bash
git clone https://github.com/ZGCA-Forge/MsgCenterPy.git
cd MsgCenterPy
pip install -e .[dev]
```

## 🔧 快速开始

### 基础使用

```python
from msgcenterpy import MessageInstance, MessageType

# 从字典创建消息实例
data = {
    "name": "sensor_001",
    "readings": [1.0, 2.0, 3.0],
    "active": True
}
dict_instance = MessageInstance.create(MessageType.DICT, data)

# 生成 JSON Schema
schema = dict_instance.get_json_schema()
print(schema)
```

### ROS2 消息转换

```python
from std_msgs.msg import String
from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

# 创建 ROS2 消息实例
string_msg = String()
string_msg.data = "Hello ROS2"
ros2_instance = ROS2MessageInstance(string_msg)

# 转换为 JSON Schema
json_schema_instance = ros2_instance.to_json_schema()

# 获取生成的 Schema
schema = json_schema_instance.json_schema
print(schema)
```

### 字段访问和约束

```python
# 动态字段访问
ros2_instance.data_field = "new_value"
print(ros2_instance.fields.get_field_info("data"))

# 类型约束验证
type_info = ros2_instance.fields.get_sub_type_info("data")
print(f"约束条件: {[c.type.value for c in type_info.constraints]}")
```

## 📖 文档

### 核心概念

- **MessageInstance**: 统一消息实例基类
- **TypeInfo**: 详细的字段类型信息和约束
- **FieldAccessor**: 统一字段访问接口
- **MessageCenter**: 消息类型管理和转换中心

### API 参考

详细的 API 文档请访问：[https://zgca-forge.github.io/MsgCenterPy/](https://zgca-forge.github.io/MsgCenterPy/)

### 示例代码

更多示例请查看 [`examples/`](examples/) 目录：

- [ROS2 消息转换示例](examples/ros2_example.py)
- [JSON Schema 生成示例](examples/json_schema_example.py)
- [类型约束示例](examples/type_constraints_example.py)

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试套件
python run_all_tests.py --type json_schema
```

```bash
# 生成覆盖率报告
pytest --cov=msgcenterpy --cov-report=html
```

## 🛠️ 开发

### 开发环境设置

```bash
git clone https://github.com/ZGCA-Forge/MsgCenterPy.git
cd MsgCenterPy
pip install -e .[dev]
pre-commit install
```

### 代码质量

```bash
# 代码格式化
black msgcenterpy tests
isort msgcenterpy tests

# 类型检查
mypy msgcenterpy

# 运行测试
pytest
```

### 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详细贡献指南请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📊 开发路线图

- [x] ✅ ROS2 消息支持
- [x] ✅ JSON Schema 生成和验证
- [x] ✅ 统一字段访问器
- [x] ✅ 类型约束系统
- [ ] 🔄 Pydantic 集成
- [ ] 🔄 Dataclass 支持
- [ ] 🔄 YAML 格式支持
- [ ] 🔄 性能优化
- [ ] 🔄 插件系统

## 🤝 社区

### 支持渠道

- 💬 讨论: [GitHub Discussions](https://github.com/ZGCA-Forge/MsgCenterPy/discussions)
- 🐛 问题: [GitHub Issues](https://github.com/ZGCA-Forge/MsgCenterPy/issues)
- 📖 文档: [GitHub Pages](https://zgca-forge.github.io/MsgCenterPy/)

### 贡献者

感谢所有为 MsgCenterPy 做出贡献的开发者！

[![Contributors](https://contrib.rocks/image?repo=ZGCA-Forge/MsgCenterPy)](https://github.com/ZGCA-Forge/MsgCenterPy/graphs/contributors)

## 📄 许可证

本项目基于 Apache-2.0 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [ROS2](https://ros.org/) - 机器人操作系统
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库
- [pytest](https://pytest.org/) - 测试框架
- [jsonschema](https://python-jsonschema.readthedocs.io/) - JSON Schema 验证

---

<div align="center">

**[⭐ 给个 Star](https://github.com/ZGCA-Forge/MsgCenterPy)** • **[🍴 Fork 项目](https://github.com/ZGCA-Forge/MsgCenterPy/fork)** • **[📖 查看文档](https://zgca-forge.github.io/MsgCenterPy/)**

Made with ❤️ by the MsgCenterPy Team

</div>
