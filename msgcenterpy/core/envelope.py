from __future__ import annotations

from typing import Any, Dict, TypedDict

ENVELOPE_VERSION: str = "1"


class Properties(TypedDict, total=False):
    ros_msg_cls_path: str
    ros_msg_cls_namespace: str
    json_schema: Dict[str, Any]
    typed_dict_class_module: str
    typed_dict_class_name: str


class FormatMetadata(TypedDict, total=False):
    """Additional metadata for source format, optional.

    Examples: field statistics, original type descriptions, field type mappings, etc.
    """

    current_format: str
    source_cls_name: str
    source_cls_module: str
    properties: Properties


class MessageEnvelope(TypedDict, total=True):
    """Unified message envelope format.

    - version: Protocol version
    - format: Source format (MessageType.value)
    - type_info: Type information (applicable for ROS2, Pydantic, etc.)
    - content: Normalized message content (dictionary)
    - metadata: Additional metadata
    """

    version: str
    format: str
    content: Dict[str, Any]
    metadata: FormatMetadata


def create_envelope(
    *,
    format_name: str,
    content: Dict[str, Any],
    metadata: FormatMetadata,
) -> MessageEnvelope:
    env: MessageEnvelope = {
        "version": ENVELOPE_VERSION,
        "format": format_name,
        "content": content,
        "metadata": metadata,
    }
    return env
