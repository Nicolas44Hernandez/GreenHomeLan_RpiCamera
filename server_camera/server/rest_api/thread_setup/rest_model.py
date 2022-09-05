"""REST API models for Thread package"""

from marshmallow import Schema
from marshmallow.fields import Str


class ThreadNetworkSetupSchema(Schema):
    """REST ressource for Thread Network setup"""

    host_ipv6_addr = Str(required=True, allow_none=False)
    host_ipv6_mesh = Str(required=True, allow_none=False)
    dataset_key = Str(required=True, allow_none=False)
    

