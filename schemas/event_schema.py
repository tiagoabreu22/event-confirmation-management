from marshmallow import Schema, fields, validate, ValidationError
import datetime


def validate_datetime(value):
    try:
        datetime.datetime.fromisoformat(value)
    except ValueError:
        raise ValidationError("Invalid datetime format")


class EventSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(required=False, validate=validate.Length(min=1))
    location = fields.Str(required=False, validate=validate.Length(min=1))
    confirmation_deadline = fields.Str(required=False, validate=validate_datetime)
    start_datetime = fields.Str(required=True, validate=validate_datetime)
    end_datetime = fields.Str(required=True, validate=validate_datetime)
    template_id = fields.Str(required=True, validate=validate.Length(min=1))
