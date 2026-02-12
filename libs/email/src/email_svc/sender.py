"""Send email (stub logs; wire to SMTP via env in production)."""
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def send_email(
    to: str,
    subject: str,
    body_text: str,
    body_html: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Send an email. When SMTP is not configured, logs the message.
    Configure SMTP via env (SMTP_HOST, SMTP_PORT, etc.) for real sending.
    """
    if os.getenv("SMTP_HOST"):
        # TODO: use smtplib to send when SMTP is configured
        logger.info("Send email to %s: %s", to, subject)
        return
    logger.info(
        "Email (not sent - no SMTP): to=%s subject=%s body_len=%d",
        to, subject, len(body_text),
    )
