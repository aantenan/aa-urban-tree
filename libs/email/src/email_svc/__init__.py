"""Email service: send transactional email (registration, password reset)."""
from email_svc.sender import send_email

__all__ = ["send_email"]
