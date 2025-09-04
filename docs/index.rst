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

MsgCenterPy is a multi-format message conversion system based on a unified instance manager architecture,
supporting seamless conversion between **ROS2**, **Pydantic**, **Dataclass**, **JSON**, **Dict**,
**YAML** and **JSON Schema**.

📦 Installation
---------------

Basic Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install msgcenterpy

With Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install ROS2 support
   conda install ros-humble-ros-core ros-humble-std-msgs ros-humble-geometry-msgs -c robostack-staging

From Source
~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/ZGCA-Forge/MsgCenterPy.git
   cd MsgCenterPy
   pip install -e .[dev]

🚀 Quick Start
--------------

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
     - 🚧
     - 🚧
     - 🚧
     - 🚧
   * - Dataclass
     - 🚧
     - 🚧
     - 🚧
     - 🚧
   * - JSON
     - 🚧
     - 🚧
     - 🚧
     - 🚧
   * - Dict
     - 🚧
     - 🚧
     - 🚧
     - 🚧
   * - YAML
     - 🚧
     - 🚧
     - 🚧
     - 🚧

.. note::
   ✅ Fully Supported | 🚧 In Development

🛠️ Development
--------------

Development Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For detailed development guidelines, please refer to the Development section.

📚 Documentation Contents
-------------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
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
