import asyncio
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Mapping, Any

import jinja2

try:
    import aiosmtplib # type: ignore
    _HAS_AIO = True
except ImportError:
    _HAS_AIO = False
    import smtplib

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Async email service with Jinja2 HTML templates."""

    def __init__(
        self,
        templates_dir: str | Path = "email_templates",
        smtp_host: str = settings.SMTP_SERVER,
        smtp_port: int = settings.SMTP_PORT,
        username: Optional[str] = settings.SMTP_USERNAME,
        password: Optional[str] = settings.SMTP_PASSWORD,
        default_from: Optional[str] = None,
        use_tls: bool = True,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.default_from = default_from or username
        self.use_tls = use_tls

        self.templates_dir = Path(templates_dir)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        self.jinja_env.filters['currency'] = lambda x: f"${x:,.2f}"

    def render_template(
        self, 
        template_name: str, 
        context: Optional[Mapping[str, Any]] = None
    ) -> str:
        """Render HTML email template."""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(context or {})
        except jinja2.TemplateNotFound:
            logger.error(f"Template not found: {template_name}")
            raise
        except jinja2.TemplateError as e:
            logger.error(f"Template error in {template_name}: {e}")
            raise

    def _create_message(
        self,
        to: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
    ) -> EmailMessage:
        """Create email message with HTML and plain text alternatives."""
        msg = EmailMessage()
        msg["From"] = from_email or self.username or self.default_from
        msg["To"] = to
        msg["Subject"] = subject

        plain_text = jinja2.filters.do_striptags(html_content).strip()
        
        msg.set_content(plain_text or "Please view this email in HTML format.")
        msg.add_alternative(html_content, subtype="html")
        
        return msg

    async def send_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: Optional[Mapping[str, Any]] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send HTML-templated email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            template_name: Jinja2 template filename (e.g., "welcome.html")
            context: Template variables
            from_email: Override default sender
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not all([self.smtp_host, self.smtp_port, self.username, self.password]):
            logger.error("SMTP configuration incomplete")
            return False

        if not to:
            logger.error("Recipient email address is required")
            return False

        try:
            html_content = self.render_template(template_name, context)
            
            msg = self._create_message(to, subject, html_content, from_email)
            
            if _HAS_AIO:
                await self._send_async(msg)
            else:
                await self._send_sync(msg)
            
            logger.info(f"Email sent to {to} (template={template_name})")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to send email to {to}: {e}")
            return False

    async def _send_async(self, msg: EmailMessage) -> None:
        """Send email using aiosmtplib (async)."""
        await aiosmtplib.send(
            msg,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.username,
            password=self.password,
            start_tls=self.use_tls,
        )

    async def _send_sync(self, msg: EmailMessage) -> None:
        """Send email using smtplib in executor (fallback)."""
        loop = asyncio.get_running_loop()
        
        def _send():
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as smtp:
                if self.use_tls:
                    smtp.starttls()
                if self.username and self.password:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg)
        
        await loop.run_in_executor(None, _send)

emailer = EmailService(
    templates_dir="src/email_templates",
    default_from="no-reply@userservice.com"
)