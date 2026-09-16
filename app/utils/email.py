"""
Outgoing email via the Brevo HTTPS API (https://brevo.com, formerly Sendinblue).

If BREVO_API_KEY isn't configured (settings.email_delivery_enabled is
False), send_email() logs the message instead of sending it. This is what
keeps local development working without real credentials — see the
EMAIL PLACEHOLDER log lines — but it also means no OTP or reset link ever
reaches a real inbox until BREVO_API_KEY is set. See .env.example.

WHY HTTPS INSTEAD OF SMTP: many free-tier hosts (Render's free web
services included) block outbound traffic on SMTP ports 25/465/587
entirely, so a perfectly-configured SMTP client would still fail there —
sometimes with an immediate "Network is unreachable", sometimes just
hanging until it times out. Brevo's API is a normal HTTPS POST (port
443), which that kind of egress firewall doesn't touch, since blocking 443
would break the app's own ability to reach its database/APIs too.

WHY BREVO SPECIFICALLY: most transactional-email providers (Resend,
SendGrid, Mailgun, Postmark, SES) require you to own and DNS-verify a
domain before they'll send to arbitrary recipients. Brevo also supports
"Single Sender Verification" — click a link emailed to a plain address
(a Gmail address works fine) and that address alone is authorized as a
From address, no domain required. That's the fit when EMAIL_FROM_EMAIL
is a Gmail address rather than something you own the DNS for.

SECURITY: never log the rendered HTML/text body in production (it may
contain an OTP or reset token) — only the subject/recipient/message-id are
logged. In dev-mode (no Brevo key configured), the body IS logged, since
that's the only way to see the code locally; that block is skipped once
BREVO_API_KEY is set.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request

from app.config import settings
from app.utils.exceptions import EmailDeliveryError

logger = logging.getLogger("laptopsathi.email")

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

# Transient network hiccups are usually gone a couple of seconds later.
# Retrying a couple of times before giving up turns an intermittent blip
# into a successful send instead of a failed registration. This only
# applies to network-level failures (timeouts, DNS, connection resets) —
# an error response *from* Brevo (unverified sender, bad payload, etc.)
# means the same request would just fail the same way again, so those are
# not retried.
_SEND_MAX_ATTEMPTS = 3
_SEND_RETRY_DELAY_SECONDS = 2


def send_email(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> None:
    """Sends an email, or logs it if Brevo isn't configured (dev mode).

    Raises EmailDeliveryError (502) if Brevo *is* configured but the send
    fails — a config/network/provider problem, not the caller's fault, so
    callers should surface a "try again" message rather than treating it
    like a validation error.
    """
    if not settings.email_delivery_enabled:
        logger.info(
            "EMAIL PLACEHOLDER (Brevo not configured — see .env BREVO_API_KEY) -> to=%s subject=%r body=%r",
            to_email, subject, text_body,
        )
        return

    payload: dict = {
        "sender": {"name": settings.EMAIL_FROM_NAME, "email": settings.EMAIL_FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_body,
    }
    if html_body:
        payload["htmlContent"] = html_body

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BREVO_API_URL,
        data=body,
        method="POST",
        headers={
            "api-key": settings.BREVO_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        message_id = _send_with_retry(request, to_email)
    except _BrevoApiError as exc:
        # A response *from* Brevo rejecting the request (unverified sender,
        # invalid payload, out of credits, etc.) — not a network problem,
        # so surface Brevo's own explanation server-side.
        logger.error(
            "Brevo rejected email to %s (HTTP %s): %s", to_email, exc.status, exc.detail,
        )
        raise EmailDeliveryError(
            "We couldn't send that email right now. Please try again in a moment."
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Never let the raw exception bubble up to the client; log it
        # server-side and return a generic message.
        logger.error("Brevo send to %s failed after %d attempt(s): %s", to_email, _SEND_MAX_ATTEMPTS, exc)
        raise EmailDeliveryError(
            "We couldn't send that email right now. Please try again in a moment."
        ) from exc

    logger.info("Email sent -> to=%s subject=%r message_id=%s", to_email, subject, message_id)


class _BrevoApiError(Exception):
    """Brevo returned a non-2xx response — a rejection, not a network failure."""

    def __init__(self, status: int, detail: str):
        super().__init__(f"Brevo API error {status}: {detail}")
        self.status = status
        self.detail = detail


def _send_with_retry(request: urllib.request.Request, to_email: str) -> str | None:
    """Returns Brevo's messageId on success. Retries network-level failures
    only; an HTTP error response from Brevo raises _BrevoApiError
    immediately without retrying, since resending the same payload would
    just get the same rejection again."""
    last_error: Exception | None = None
    for attempt in range(1, _SEND_MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=settings.BREVO_TIMEOUT_SECONDS) as response:
                data = json.loads(response.read().decode("utf-8") or "{}")
                return data.get("messageId")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise _BrevoApiError(exc.code, detail) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < _SEND_MAX_ATTEMPTS:
                logger.warning(
                    "Brevo send to %s failed on attempt %d/%d (%s) — retrying in %ds",
                    to_email, attempt, _SEND_MAX_ATTEMPTS, exc, _SEND_RETRY_DELAY_SECONDS,
                )
                time.sleep(_SEND_RETRY_DELAY_SECONDS)
    raise last_error


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
