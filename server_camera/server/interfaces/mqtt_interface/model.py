"""
MQTT messages model
"""

from typing import TypeVar
import bson

Msg = TypeVar("Msg")


def serialize(msg: Msg) -> bytes:
    """serialize MQTT message"""
    if type(msg) is dict:
        data_to_send = msg
    else:
        data_to_send = msg.to_json()
    return bson.dumps(data_to_send)


def deserialize(payload: bytes) -> Msg:
    """deserialize MQTT message"""
    # TODO: review
    return bson.loads(payload)

