Installation Guide
==================

This guide will help you install MsgCenterPy in different environments.

Quick Installation
------------------

The easiest way to install MsgCenterPy is using pip:

.. code-block:: bash

   pip install msgcenterpy

Requirements
------------

- Python 3.10 or higher (Python 3.11+ recommended for optimal ROS2 compatibility)
- Operating System: Linux, macOS, or Windows

Optional Dependencies
---------------------

ROS2 Support
~~~~~~~~~~~~

To use ROS2 message conversion features:

.. code-block:: bash

   pip install msgcenterpy[ros2]

This will install:
- ``rosidl-runtime-py>=0.10.0``
- ``rclpy>=3.0.0``

.. warning::
   **ROS2 Python Version Compatibility Notice**

   While Python 3.10+ is supported by this package, ROS2 official binary distributions
   may have varying support across Python versions. You might need to:

   - Build ROS2 from source for newer Python versions
   - Use ROS2 distributions that officially support your Python version
   - Consider using conda-forge ROS2 packages if available

   For production environments, verify ROS2 compatibility in your specific setup.

Development Tools
~~~~~~~~~~~~~~~~~

For development and testing:

.. code-block:: bash

   pip install msgcenterpy[dev]

This includes:
- ``pytest>=7.0.0``
- ``black>=22.0.0``
- ``isort>=5.0.0``
- ``mypy>=1.0.0``
- ``pre-commit>=2.20.0``

Documentation Tools
~~~~~~~~~~~~~~~~~~~

For building documentation:

.. code-block:: bash

   pip install msgcenterpy[docs]

All Dependencies
~~~~~~~~~~~~~~~~

To install all optional dependencies:

.. code-block:: bash

   pip install msgcenterpy[all]

From Source
-----------

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

To install from source for development:

.. code-block:: bash

   git clone https://github.com/ZGCA-Forge/MsgCenterPy.git
   cd MsgCenterPy
   pip install -e .[dev]

This will install the package in development mode, allowing you to make changes to the source code.

Verification
------------

To verify your installation:

.. code-block:: python

   import msgcenterpy
   print(msgcenterpy.get_version())
   print(msgcenterpy.check_dependencies())

The output should show the version number and available dependencies.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **Python Version**: Ensure you're using Python 3.10 or higher (3.11+ recommended for optimal ROS2 compatibility)
2. **ROS2 Dependencies**: ROS2 support requires a proper ROS2 installation
3. **Virtual Environments**: Consider using virtual environments for isolation

If you encounter any issues, please check the `GitHub Issues <https://github.com/ZGCA-Forge/MsgCenterPy/issues>`_ page.
