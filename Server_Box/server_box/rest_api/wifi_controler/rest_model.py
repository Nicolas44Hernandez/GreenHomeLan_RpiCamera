"""REST API models for wifi bands manager package"""

from marshmallow import Schema
from marshmallow.fields import Int, DateTime, String, Nested, Float, List, Str, Bool

class WifiStatusSchema(Schema):
    """REST ressource for wifi and bands status"""
    status = Bool(required=True, allow_none=False)