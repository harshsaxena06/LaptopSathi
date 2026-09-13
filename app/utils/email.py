"""
Outgoing email via SMTP — works with any provider (Gmail, SendGrid,
Mailgun, Amazon SES, Postmark, your own mail server, ...) since they all
speak standard SMTP. No provider-specific SDK, so there's nothing to swap
out if you change providers later — just the .env values.

If SMTP_HOST isn't configured (settings.email_delivery_enabled is False),
send_email() logs the message instead of sending it. This is what keeps
local development working without real credentials — see the
EMAIL PLACEHOLDER log lines — but it also means no OTP or reset link ever
reaches a real inbox until SMTP_HOST etc. are set. See .env.example.

SECURITY: never log the rendered HTML/text body in production (it may
contain an OTP or reset token) — only the subject/recipient/message-id are
logged. In dev-mode (no SMTP configured), the body IS logged, since that's
the only way to see the code locally; that block is skipped once SMTP_HOST
is set.
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

from app.config import settings
from app.utils.exceptions import EmailDeliveryError

logger = logging.getLogger("laptopsathi.email")


def send_email(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> None:
    """Sends an email, or logs it if SMTP isn't configured (dev mode).

    Raises EmailDeliveryError (502) if SMTP *is* configured but the send
    fails — a config/network/provider problem, not the caller's fault, so
    callers should surface a "try again" message rather than treating it
    like a validation error.
    """
    if not settings.email_delivery_enabled:
        logger.info(
            "EMAIL PLACEHOLDER (SMTP not configured — see .env SMTP_HOST) -> to=%s subject=%r body=%r",
            to_email, subject, text_body,
        )
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Message-ID"] = make_msgid(domain=settings.SMTP_FROM_EMAIL.split("@")[-1] or None)
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT_SECONDS) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError, TimeoutError) as exc:
        # Never let the raw exception (which can embed SMTP server responses)
        # bubble up to the client; log it server-side and return a generic message.
        logger.error("SMTP send to %s failed: %s", to_email, exc)
        raise EmailDeliveryError(
            "We couldn't send that email right now. Please try again in a moment."
        ) from exc

    logger.info("Email sent -> to=%s subject=%r message_id=%s", to_email, subject, message["Message-ID"])


# ---------------------------------------------------------------------------
# Templates — kept simple (inline HTML, no template engine dependency) since
# there are only a couple of transactional emails. Add more render_* helpers
# here as needed rather than building strings in the router.
# ---------------------------------------------------------------------------

def _wrap_html(inner_html: str) -> str:
    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background:#f4f4f7;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:12px;padding:32px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
            <tr><td style="font-size:18px;font-weight:700;color:#111827;padding-bottom:20px;">LaptopSathi AI</td></tr>
            {inner_html}
            <tr><td style="padding-top:28px;font-size:12px;color:#9ca3af;">
              If you didn't request this, you can safely ignore this email.
            </td></tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def render_registration_otp_email(otp: str, expire_minutes: int) -> tuple[str, str, str]:
    """Returns (subject, text_body, html_body)."""
    subject = f"{otp} is your LaptopSathi verification code"
    text_body = (
        f"Your LaptopSathi verification code is: {otp}\n\n"
        f"Enter this code to finish creating your account. It expires in {expire_minutes} minutes.\n\n"
        "If you didn't try to create a LaptopSathi account, you can ignore this email."
    )
    html_body = _wrap_html(f"""
      <tr><td style="font-size:15px;color:#374151;padding-bottom:20px;">
        Enter this code to finish creating your account:
      </td></tr>
      <tr><td align="center" style="padding-bottom:20px;">
        <div style="display:inline-block;font-size:32px;font-weight:700;letter-spacing:8px;
                    color:#111827;background:#f4f4f7;border-radius:8px;padding:16px 24px;">{otp}</div>
      </td></tr>
      <tr><td style="font-size:13px;color:#6b7280;">This code expires in {expire_minutes} minutes.</td></tr>
    """)
    return subject, text_body, html_body


def render_password_reset_email(reset_url: str) -> tuple[str, str, str]:
    subject = "Reset your LaptopSathi password"
    text_body = (
        "We received a request to reset your LaptopSathi password.\n\n"
        f"Reset it here: {reset_url}\n\n"
        "If you didn't request this, you can ignore this email — your password won't change."
    )
    html_body = _wrap_html(f"""
      <tr><td style="font-size:15px;color:#374151;padding-bottom:20px;">
        We received a request to reset your password. Click below to choose a new one.
      </td></tr>
      <tr><td align="center" style="padding-bottom:20px;">
        <a href="{reset_url}"
           style="display:inline-block;background:#111827;color:#ffffff;text-decoration:none;
                  font-size:14px;font-weight:600;border-radius:8px;padding:12px 24px;">
          Reset password
        </a>
      </td></tr>
      <tr><td style="font-size:13px;color:#6b7280;word-break:break-all;">
        Or paste this link into your browser: {reset_url}
      </td></tr>
    """)
    return subject, text_body, html_body
