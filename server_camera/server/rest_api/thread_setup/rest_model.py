"""REST API models for Thread package"""

from marshmallow import Schema
from marshmallow.fields import Str


class ThreadNetworkSetupSchema(Schema):
    """REST ressource for Thread Network setup"""

    ipv6_otbr = Str(required=True, allow_none=False)
    ipv6_mesh = Str(required=True, allow_none=False)
    dataset_key = Str(required=True, allow_none=False)
