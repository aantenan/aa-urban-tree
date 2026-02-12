"""Email service abstraction: interface, console (dev), SMTP (production)."""
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class EmailService(Protocol):
    """Interface for sending email. Use ConsoleEmailService in dev, SmtpEmailService in production."""

    def send(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Send an email. Raises on failure in production; logs only in dev."""
        ...


class ConsoleEmailService:
    """Development: log email to console instead of sending."""

    def send(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
        **kwargs: Any,
    ) -> None:
        logger.info(
            "Email (console): to=%s subject=%s body_len=%d",
            to, subject, len(body_text),
        )


class SmtpEmailService:
    """Production: send email via SMTP. Configure with SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
    ) -> None:
        self.host = host or os.getenv("SMTP_HOST", "")
        self.port = port or int(os.getenv("SMTP_PORT", "587"))
        self.user = user or os.getenv("SMTP_USER", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.use_tls = use_tls

    def send(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not self.host:
            logger.warning("SMTP not configured; logging email instead")
            logger.info("Email: to=%s subject=%s", to, subject)
            return
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.user or "noreply@localhost"
        msg["To"] = to
        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            if self.user and self.password:
                server.login(self.user, self.password)
            server.sendmail(msg["From"], to, msg.as_string())
        logger.info("Email sent to %s: %s", to, subject)
