Quick Start Guide
=================

This guide will get you up and running with MsgCenterPy in just a few minutes.

First Steps
-----------

After installation, you can start using MsgCenterPy immediately:

.. code-block:: python

   from msgcenterpy import MessageInstance, MessageType

   # Create a simple message from dictionary
   data = {"name": "test", "value": 42}
   instance = MessageInstance.create(MessageType.DICT, data)

   # Get JSON Schema
   schema = instance.get_json_schema()
   print(schema)

Basic Concepts
--------------

MessageInstance
~~~~~~~~~~~~~~~

The core concept in MsgCenterPy is the ``MessageInstance``, which provides a unified interface for different message formats.

.. code-block:: python

   from msgcenterpy import MessageInstance, MessageType

   # Different ways to create instances
   dict_instance = MessageInstance.create(MessageType.DICT, {"key": "value"})

   # Access fields
   print(dict_instance.get_field("key"))

MessageType
~~~~~~~~~~~

MsgCenterPy supports various message types:

- ``MessageType.DICT``: Python dictionaries
- ``MessageType.JSON_SCHEMA``: JSON Schema objects
- ``MessageType.ROS2``: ROS2 messages (with optional dependency)

Working with ROS2 Messages
---------------------------

If you have ROS2 installed, you can work with ROS2 messages:

.. code-block:: python

   from std_msgs.msg import String
   from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

   # Create ROS2 message
   msg = String()
   msg.data = "Hello ROS2"

   # Create instance
   ros2_instance = ROS2MessageInstance(msg)

   # Convert to JSON Schema
   json_schema_instance = ros2_instance.to_json_schema()
   print(json_schema_instance.json_schema)

JSON Schema Generation
----------------------

One of the key features is automatic JSON Schema generation:

.. code-block:: python

   from msgcenterpy import MessageInstance, MessageType

   # Complex nested structure
   data = {
       "sensor": {
           "name": "temperature_01",
           "readings": [23.5, 24.1, 23.8],
           "metadata": {
               "unit": "celsius",
               "precision": 0.1
           }
       }
   }

   instance = MessageInstance.create(MessageType.DICT, data)
   schema = instance.get_json_schema()

   # The schema will include type information for all nested structures

Field Access and Type Information
----------------------------------

MsgCenterPy provides detailed type information and field access:

.. code-block:: python

   # Access field information
   field_info = instance.fields.get_field_info("sensor.name")
   print(f"Field type: {field_info.type}")
   print(f"Field constraints: {field_info.constraints}")

   # Dynamic field access
   instance.set_field("sensor.name", "temperature_02")
   value = instance.get_field("sensor.name")

Error Handling
--------------

MsgCenterPy includes comprehensive error handling:

.. code-block:: python

   try:
       # Invalid field access
       value = instance.get_field("nonexistent.field")
   except FieldAccessError as e:
       print(f"Field access error: {e}")

   try:
       # Type constraint violation
       instance.set_field("sensor.readings", "invalid")
   except TypeConstraintError as e:
       print(f"Type error: {e}")

Next Steps
----------

- Read the :doc:`user_guide/index` for detailed usage
- Check out :doc:`examples/basic_usage` for more examples
- Explore the :doc:`api/core` documentation
- Learn about :doc:`development/contributing` if you want to contribute
