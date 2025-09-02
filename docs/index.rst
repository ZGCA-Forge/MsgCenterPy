Welcome to MsgCenterPy's Documentation!
========================================

.. image:: https://img.shields.io/badge/license-Apache--2.0-blue.svg
   :target: https://github.com/ZGCA-Forge/MsgCenterPy/blob/main/LICENSE
   :alt: License

.. image:: https://img.shields.io/pypi/v/msgcenterpy.svg
   :target: https://pypi.org/project/msgcenterpy/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/msgcenterpy.svg
   :target: https://pypi.org/project/msgcenterpy/
   :alt: Python versions

MsgCenterPy is a unified message conversion system based on unified instance manager architecture,
supporting seamless conversion between **ROS2**, **Pydantic**, **Dataclass**, **JSON**, **Dict**,
**YAML** and **JSON Schema**.

✨ Key Features
---------------

🔄 **Unified Conversion**: Supports bidirectional conversion between multiple message formats

🤖 **ROS2 Integration**: Complete support for ROS2 message types and constraints

📊 **JSON Schema**: Automatic generation and validation of JSON Schema

🏗️ **Type Safety**: Strong type constraint system based on TypeInfo

🔍 **Field Access**: Unified field accessor interface

⚡ **High Performance**: Optimized conversion algorithms and caching mechanism

🧪 **Complete Testing**: 47+ test cases with >90% coverage

📦 Quick Start
--------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install msgcenterpy

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from msgcenterpy import MessageInstance, MessageType

   # Create message instance from dictionary
   data = {
       "name": "sensor_001",
       "readings": [1.0, 2.0, 3.0],
       "active": True
   }
   dict_instance = MessageInstance.create(MessageType.DICT, data)

   # Generate JSON Schema
   schema = dict_instance.get_json_schema()
   print(schema)

🎯 Supported Formats
--------------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Format
     - Read
     - Write
     - JSON Schema
     - Type Constraints
   * - ROS2
     - ✅
     - ✅
     - ✅
     - ✅
   * - JSON Schema
     - ✅
     - ✅
     - ✅
     - ✅
   * - Pydantic
     - 开发中
     - 开发中
     - 开发中
     - 开发中
   * - Dataclass
     - 开发中
     - 开发中
     - 开发中
     - 开发中
   * - JSON
     - 开发中
     - 开发中
     - ✅
     - ⚡
   * - Dict
     - 开发中
     - 开发中
     - ✅
     - ⚡
   * - YAML
     - 开发中
     - 开发中
     - ✅
     - ⚡

.. note::
   ✅ Fully Supported | 开发中 In Development | ⚡ Basic Support

📚 Documentation Contents
-------------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   user_guide/index

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic_usage
   examples/ros2_examples
   examples/json_schema_examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/instances
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/contributing
   development/testing
   development/changelog

.. toctree::
   :maxdepth: 1
   :caption: Community

   community/support
   community/faq

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

🤝 Community & Support
======================

- 📖 **Documentation**: https://zgca-forge.github.io/MsgCenterPy/
- 🐛 **Issues**: https://github.com/ZGCA-Forge/MsgCenterPy/issues
- 💬 **Discussions**: https://github.com/ZGCA-Forge/MsgCenterPy/discussions

📄 License
==========

This project is licensed under the Apache-2.0 License - see the `LICENSE <https://github.com/ZGCA-Forge/MsgCenterPy/blob/main/LICENSE>`_ file for details.
