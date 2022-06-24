"""REST API models for wifi bands manager package"""

from marshmallow import Schema
from marshmallow.fields import Bool

class WifiStatusSchema(Schema):
    """REST ressource for wifi and bands status"""
    status = Bool(required=True, allow_none=False)