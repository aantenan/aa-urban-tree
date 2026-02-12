"""Password reset token model."""
from peewee import DateTimeField, ForeignKeyField, CharField

from database.models.base import BaseModel
from database.models.user import User


class PasswordReset(BaseModel):
    """Password reset request: user, token, expires_at, used_at."""

    user = ForeignKeyField(User, backref="password_resets")
    reset_token = CharField(unique=True, index=True, max_length=255)
    expires_at = DateTimeField()
    used_at = DateTimeField(null=True)

    class Meta:
        table_name = "password_resets"
