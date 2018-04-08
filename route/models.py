from datetime import datetime
from umongo import Document, fields, EmbeddedDocument
from marshmallow import validate
from app import MetaBaseTemplate


class Vector(EmbeddedDocument, metaclass=MetaBaseTemplate):

    VEHICLE = 0
    FOOT = 1
    AIR = 2
    BIKE = 3

    points = fields.ListField(fields.DictField, required=True)
    types = fields.ListField(
        fields.IntegerField,
        validate=validate.ContainsOnly([VEHICLE, FOOT, AIR, BIKE]))


class Route(Document, metaclass=MetaBaseTemplate):
    author = fields.UUIDField(required=True)
    title = fields.StringField(validate=validate.Length(max=255), required=True)
    vectors = fields.ListField(fields.EmbeddedField(Vector), missing=list)
    is_public = fields.BooleanField(missing=False, default=False)
    created = fields.DateTimeField(missing=datetime.utcnow)

    class Meta:
        collection_name = "routes"


class RoutePoint(Document, metaclass=MetaBaseTemplate):
    route = fields.ReferenceField(Route, required=True)
    point = fields.DictField(required=True)
    photos = fields.ListField(fields.ObjectIdField, missing=list)
    text = fields.StringField()
    tags = fields.ListField(fields.StringField, missing=list)
    liked = fields.IntegerField(missing=0)

    class Meta:
        collection_name = "route_points"
