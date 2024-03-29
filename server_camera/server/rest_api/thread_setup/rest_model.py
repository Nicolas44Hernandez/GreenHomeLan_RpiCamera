"""REST API models for Thread package"""

from marshmallow import Schema
from marshmallow.fields import Str


class ThreadNetworkSetupSchema(Schema):
    """REST ressource for Thread Network setup"""

    ipv6_mesh = Str(required=True, allow_none=False)
    dataset_key = Str(required=True, allow_none=False)


class ThreadMessageSchema(Schema):
    """REST ressource for Thread message"""

    message = Str(required=True, allow_none=False)
