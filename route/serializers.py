from marshmallow import fields, Schema

class UserSchema(Schema):
    email = fields.Email()
    guid = fields.UUID()
    name = fields.String()


class UserTopSchema(Schema):
    _id = fields.UUID(dump_only=True, dump_to="author")
    count = fields.Integer(dump_only=True)
    user = fields.Nested(UserSchema(dump_only=("email", "guid", "name")))

