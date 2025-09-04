Basic Usage Examples
====================

This page contains basic usage examples to help you get started with MsgCenterPy.

Creating Message Instances
---------------------------

ROS2 Message Instances
----------------------

Working with ROS2 Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from msgcenterpy.instances.ros2_instance import ROS2MessageInstance
   from std_msgs.msg import String, Float64MultiArray
   from geometry_msgs.msg import Point, Pose

   # Simple String message
   string_msg = String()
   string_msg.data = "Hello ROS2"
   ros2_instance = ROS2MessageInstance(string_msg)

   # Access and modify field
   ros2_instance.data = "Updated message"
   print(f"Message data: {ros2_instance.inner_data.data}")

   # Float array message
   array_msg = Float64MultiArray()
   array_msg.data = [1.1, 2.2, 3.3, 4.4, 5.5]
   array_instance = ROS2MessageInstance(array_msg)

   # Complex nested message
   pose_msg = Pose()
   pose_instance = ROS2MessageInstance(pose_msg)

   # Set nested fields
   pose_instance.position.x = 1.5
   pose_instance.position.y = 2.5
   pose_instance.position.z = 3.5

   # Or set entire object
   new_position = Point(x=10.0, y=20.0, z=30.0)
   pose_instance.position = new_position

Converting ROS2 to Python Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get Python dictionary representation
   python_dict = ros2_instance.get_python_dict()
   print(f"Dictionary: {python_dict}")

   # Set data from dictionary
   new_data = {"data": "dictionary_value"}
   ros2_instance.set_python_dict(new_data)


JSON Schema Message Instances
-----------------------------

Creating JSON Schema Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from msgcenterpy.instances.json_schema_instance import JSONSchemaMessageInstance

   # Define JSON Schema
   schema = {
       "type": "object",
       "properties": {
           "name": {"type": "string", "minLength": 2, "maxLength": 50},
           "age": {"type": "integer", "minimum": 0, "maximum": 150},
           "active": {"type": "boolean"},
           "tags": {
               "type": "array",
               "items": {"type": "string"},
               "minItems": 1,
               "maxItems": 10
           }
       },
       "required": ["name"]
   }

   # Sample data
   data = {
       "name": "John Doe",
       "age": 30,
       "active": True,
       "tags": ["developer", "python"]
   }

   # Create instance
   json_schema_instance = JSONSchemaMessageInstance(data, schema)

Working with JSON Schema Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get field type information with constraints
   name_type_info = json_schema_instance.fields.get_sub_type_info("name")
   print(f"Field type: {name_type_info.standard_type}")
   print(f"Min length: {name_type_info.get_constraint_value('min_length')}")

   # Check validation errors
   if len(json_schema_instance._validation_errors) == 0:
       print("Data is valid according to schema")
   else:
       print(f"Validation errors: {json_schema_instance._validation_errors}")

   # Export to envelope format
   envelope = json_schema_instance.export_to_envelope()
   print(f"Envelope metadata: {envelope['metadata']}")

Message Type Conversion
-----------------------

Converting ROS2 to JSON Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from std_msgs.msg import String
   from msgcenterpy.instances.ros2_instance import ROS2MessageInstance

   # Create ROS2 instance
   string_msg = String()
   string_msg.data = "conversion_test"
   ros2_instance = ROS2MessageInstance(string_msg)

   # Convert to JSON Schema instance
   json_schema_instance = ros2_instance.to_json_schema()

   # Verify conversion
   print(f"Original data: {ros2_instance.get_python_dict()}")
   print(f"Converted data: {json_schema_instance.get_python_dict()}")
   print(f"Generated schema: {json_schema_instance.json_schema}")

Generate JSON Schema from ROS2 Message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from geometry_msgs.msg import Pose

   # Create complex ROS2 message
   pose_msg = Pose()
   pose_msg.position.x = 5.0
   pose_msg.position.y = 10.0
   pose_msg.position.z = 15.0
   pose_msg.orientation.w = 1.0

   ros2_instance = ROS2MessageInstance(pose_msg)

   # Generate JSON Schema
   schema = ros2_instance.get_json_schema()

   print("Generated JSON Schema:")
   print(f"Type: {schema['type']}")
   print(f"Properties: {list(schema['properties'].keys())}")
   print(f"Position schema: {schema['properties']['position']}")
