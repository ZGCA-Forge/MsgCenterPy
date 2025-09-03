Installation Guide
==================

This guide will help you install MsgCenterPy in different environments.

Basic Installation
-------------------

The easiest way to install MsgCenterPy is using pip:

.. code-block:: bash

   pip install msgcenterpy

Requirements
------------

- Python 3.10 or higher (Python 3.11+ recommended for optimal ROS2 compatibility)
- Operating System: Linux, macOS, or Windows

With Optional Dependencies
--------------------------

ROS2 Support
~~~~~~~~~~~~

To use ROS2 message conversion features, install ROS2 packages via conda:

.. code-block:: bash

   # Install ROS2 support
   conda install ros-humble-ros-core ros-humble-std-msgs ros-humble-geometry-msgs -c robostack-staging

This provides the necessary ROS2 packages for message type conversion and integration.

.. note::
   **ROS2 Installation Notes**

   - We recommend using conda with the robostack-staging channel for ROS2 packages
   - This approach provides better Python version compatibility
   - Alternative ROS2 installation methods are also supported if you have them set up

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **Python Version**: Ensure you're using Python 3.10 or higher (3.11.11 recommended for 0.6.x ROS2 compatibility)
2. **ROS2 Dependencies**: ROS2 support requires a proper ROS2 installation
3. **Virtual Environments**: Consider using virtual environments for isolation

If you encounter any issues, please check the `GitHub Issues <https://github.com/ZGCA-Forge/MsgCenterPy/issues>`_ page.
