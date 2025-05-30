from marshmallow import Schema, fields

class PostSubmitSchema(Schema):
    postContent = fields.Str(dump_only=True)
    postBase64 = fields.Str(dump_only=True)