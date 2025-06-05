from marshmallow import Schema, fields

class PostSubmitSchema(Schema):
    userAddress = fields.Str(load_only=True)
    postContent = fields.Str(load_only=True)
    postBase64 = fields.Str(load_only=True)
    signedMessage = fields.Str(load_only=True)

class RegisterDataSchema(Schema):
    walletAddress = fields.Str(load_only=True)
    signedMessage = fields.Str(load_only=True)
    username = fields.Str(load_only=True)