# MsgCenterPy

<div align="center">

[![PyPI version](https://badge.fury.io/py/msgcenterpy.svg)](https://badge.fury.io/py/msgcenterpy)
[![Python versions](https://img.shields.io/pypi/pyversions/msgcenterpy.svg)](https://pypi.org/project/msgcenterpy/)
[![Build Status](https://github.com/ZGCA-Forge/MsgCenterPy/actions/workflows/ci.yml/badge.svg)](https://github.com/ZGCA-Forge/MsgCenterPy/actions)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-brightgreen)](https://zgca-forge.github.io/MsgCenterPy/)

[![GitHub stars](https://img.shields.io/github/stars/ZGCA-Forge/MsgCenterPy.svg?style=social&label=Star)](https://github.com/ZGCA-Forge/MsgCenterPy)
[![GitHub forks](https://img.shields.io/github/forks/ZGCA-Forge/MsgCenterPy.svg?style=social&label=Fork)](https://github.com/ZGCA-Forge/MsgCenterPy/fork)
[![GitHub issues](https://img.shields.io/github/issues/ZGCA-Forge/MsgCenterPy.svg)](https://github.com/ZGCA-Forge/MsgCenterPy/issues)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/ZGCA-Forge/MsgCenterPy/blob/main/LICENSE)

</div>

---

MsgCenterPy is a multi-format message conversion system based on a unified instance manager architecture, supporting seamless conversion between **ROS2**, **Pydantic**, **Dataclass**, **JSON**, **Dict**, **YAML**, and **JSON Schema**.

### Supported Formats

| Format      | Read | Write | JSON Schema | Type Constraints |
| ----------- | ---- | ----- | ----------- | ---------------- |
| ROS2        | ✅   | ✅    | ✅          | ✅               |
| JSON Schema | ✅   | ✅    | ✅          | ✅               |
| Pydantic    | 🚧   | 🚧    | 🚧          | 🚧               |
| Dataclass   | 🚧   | 🚧    | 🚧          | 🚧               |
| JSON        | 🚧   | 🚧    | 🚧          | 🚧               |
| Dict        | 🚧   | 🚧    | 🚧          | 🚧               |
| YAML        | 🚧   | 🚧    | 🚧          | 🚧               |

## Installation

### Basic Installation

```bash
pip install msgcenterpy
```

### With Optional Dependencies

```bash
# Install ROS2 support
conda install ros-humble-ros-core ros-humble-std-msgs ros-humble-geometry-msgs -c robostack-staging
```

### From Source

```bash
git clone https://github.com/ZGCA-Forge/MsgCenterPy.git
cd MsgCenterPy
pip install -e .[dev]
```

## Quick Start

Please visit: [https://zgca-forge.github.io/MsgCenterPy/](https://zgca-forge.github.io/MsgCenterPy/)

## Development

### Development Environment Setup

```bash
git clone https://github.com/ZGCA-Forge/MsgCenterPy.git
cd MsgCenterPy
pip install -e .[dev]
pre-commit install
```

For API documentation, please refer to Quick Start

## License

This project is licensed under Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by the MsgCenterPy Team

</div>
