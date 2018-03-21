from marshmallow import fields, Schema


class UserTopSchema(Schema):
    _id = fields.UUID(dump_only=True, dump_to="author")
    count = fields.Integer(dump_only=True)
