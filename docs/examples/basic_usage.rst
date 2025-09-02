Basic Usage Examples
====================

This page contains basic usage examples to help you get started with MsgCenterPy.

Creating Message Instances
---------------------------

Dictionary Messages
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from msgcenterpy import MessageInstance, MessageType

   # Simple dictionary
   simple_data = {"name": "sensor_01", "active": True}
   instance = MessageInstance.create(MessageType.DICT, simple_data)

   # Access fields
   name = instance.get_field("name")
   print(f"Sensor name: {name}")

   # Nested dictionary
   nested_data = {
       "device": {
           "id": "dev_001",
           "sensors": [
               {"type": "temperature", "value": 23.5},
               {"type": "humidity", "value": 65.2}
           ]
       }
   }
   nested_instance = MessageInstance.create(MessageType.DICT, nested_data)

JSON Schema Generation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Generate JSON Schema from dictionary
   schema = instance.get_json_schema()
   print("Generated Schema:")
   print(schema)

   # Schema includes type information
   assert schema["type"] == "object"
   assert "name" in schema["properties"]
   assert schema["properties"]["name"]["type"] == "string"

Field Access and Manipulation
------------------------------

Getting Field Values
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Simple field access
   name = instance.get_field("name")

   # Nested field access using dot notation
   device_id = nested_instance.get_field("device.id")
   temp_value = nested_instance.get_field("device.sensors.0.value")

Setting Field Values
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Set simple field
   instance.set_field("name", "sensor_02")

   # Set nested field
   nested_instance.set_field("device.id", "dev_002")
   nested_instance.set_field("device.sensors.0.value", 24.1)

Working with Field Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get field type information
   field_info = instance.fields.get_field_info("name")
   print(f"Field type: {field_info.type}")
   print(f"Field constraints: {field_info.constraints}")

   # Check if field exists
   if instance.fields.has_field("name"):
       print("Field 'name' exists")

Type Constraints and Validation
-------------------------------

.. code-block:: python

   from msgcenterpy.core.types import TypeConstraintError

   try:
       # This will raise an error if type doesn't match
       instance.set_field("active", "not_a_boolean")
   except TypeConstraintError as e:
       print(f"Type constraint violation: {e}")

   # Type conversion when possible
   instance.set_field("name", 123)  # Converts to string if allowed

Message Conversion
------------------

Converting Between Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create from dictionary
   dict_instance = MessageInstance.create(MessageType.DICT, {"key": "value"})

   # Convert to JSON Schema instance
   schema_instance = dict_instance.to_json_schema()

   # Get the actual schema
   schema = schema_instance.json_schema
   print(schema)

Error Handling
--------------

Common Error Scenarios
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from msgcenterpy.core.exceptions import FieldAccessError, TypeConstraintError

   # Field access errors
   try:
       value = instance.get_field("nonexistent_field")
   except FieldAccessError as e:
       print(f"Field not found: {e}")

   # Type constraint errors
   try:
       instance.set_field("active", "invalid_boolean")
   except TypeConstraintError as e:
       print(f"Invalid type: {e}")

   # Graceful handling
   def safe_get_field(instance, field_name, default=None):
       try:
           return instance.get_field(field_name)
       except FieldAccessError:
           return default

   # Usage
   value = safe_get_field(instance, "optional_field", "default_value")

Best Practices
--------------

1. **Always handle exceptions** when accessing fields that might not exist
2. **Use type hints** in your code for better development experience
3. **Validate data** before creating instances when working with external data
4. **Use dot notation** for nested field access instead of manual dictionary traversal
5. **Check field existence** before accessing optional fields

Complete Example
----------------

Here's a complete example that demonstrates multiple features:

.. code-block:: python

   from msgcenterpy import MessageInstance, MessageType
   from msgcenterpy.core.exceptions import FieldAccessError, TypeConstraintError
   import json

   def process_sensor_data(sensor_data):
       """Process sensor data with proper error handling."""
       try:
           # Create instance
           instance = MessageInstance.create(MessageType.DICT, sensor_data)

           # Validate required fields
           required_fields = ["id", "type", "readings"]
           for field in required_fields:
               if not instance.fields.has_field(field):
                   raise ValueError(f"Missing required field: {field}")

           # Process readings
           readings = instance.get_field("readings")
           if isinstance(readings, list) and len(readings) > 0:
               avg_reading = sum(readings) / len(readings)
               instance.set_field("average", avg_reading)

           # Generate schema for validation
           schema = instance.get_json_schema()

           # Return processed data and schema
           return {
               "processed_data": instance.to_dict(),
               "schema": schema,
               "success": True
           }

       except (FieldAccessError, TypeConstraintError, ValueError) as e:
           return {
               "error": str(e),
               "success": False
           }

   # Usage
   sensor_data = {
       "id": "temp_001",
       "type": "temperature",
       "readings": [23.1, 23.5, 24.0, 23.8],
       "unit": "celsius"
   }

   result = process_sensor_data(sensor_data)
   if result["success"]:
       print("Processing successful!")
       print(f"Average reading: {result['processed_data']['average']}")
   else:
       print(f"Processing failed: {result['error']}")
