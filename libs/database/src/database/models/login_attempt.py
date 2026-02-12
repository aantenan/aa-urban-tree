"""Login attempt tracking for lockout and audit."""
from datetime import datetime

from peewee import BooleanField, CharField, DateTimeField

from database.models.base import BaseModel


class LoginAttempt(BaseModel):
    """Record of a login attempt: email, time, success, optional ip_address."""

    email = CharField(index=True, max_length=255)
    attempt_time = DateTimeField(default=datetime.utcnow)
    success = BooleanField()
    ip_address = CharField(max_length=45, null=True)  # IPv6 max length

    class Meta:
        table_name = "login_attempts"
