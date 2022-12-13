"""REST API models for Wifi connection package"""

from marshmallow import Schema
from marshmallow.fields import Str, Bool


class WifiConnectionSchema(Schema):
    """REST ressource for Wifi connection status"""

    connected = Bool(required=True, allow_none=False)
