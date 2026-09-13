"""
Tests for app.utils.email — the real SMTP send path is exercised with
smtplib.SMTP mocked out (no real network calls), and the dev-mode fallback
(no SMTP configured) is exercised for real since it only logs.
"""
import logging
from unittest.mock import MagicMock, patch

import pytest

from app.utils.email import send_email, render_registration_otp_email, render_password_reset_email
from app.utils.exceptions import EmailDeliveryError


class _FakeSettings:
    email_delivery_enabled = False
    SMTP_HOST = ""
    SMTP_PORT = 587
    SMTP_USERNAME = ""
    SMTP_PASSWORD = ""
    SMTP_USE_TLS = True
    SMTP_FROM_EMAIL = "no-reply@laptopsathi.ai"
    SMTP_FROM_NAME = "LaptopSathi AI"
    SMTP_TIMEOUT_SECONDS = 10


def test_dev_mode_logs_instead_of_sending(caplog):
    fake = _FakeSettings()
    fake.email_delivery_enabled = False
    with patch("app.utils.email.settings", fake):
        with caplog.at_level(logging.INFO):
            send_email("alice@example.com", "Subject", "Your code is 123456")
    assert any("EMAIL PLACEHOLDER" in r.getMessage() for r in caplog.records)
    assert any("123456" in r.getMessage() for r in caplog.records)


def test_real_send_calls_smtp_with_correct_recipient_and_credentials():
    fake = _FakeSettings()
    fake.email_delivery_enabled = True
    fake.SMTP_HOST = "smtp.example.com"
    fake.SMTP_PORT = 587
    fake.SMTP_USERNAME = "apikey"
    fake.SMTP_PASSWORD = "secret"
    fake.SMTP_USE_TLS = True

    mock_smtp_instance = MagicMock()
    mock_smtp_instance.__enter__.return_value = mock_smtp_instance
    mock_smtp_instance.__exit__.return_value = False

    with patch("app.utils.email.settings", fake), \
         patch("app.utils.email.smtplib.SMTP", return_value=mock_smtp_instance) as mock_smtp_cls:
        send_email("alice@example.com", "Verify your account", "text body", "<p>html body</p>")

    mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("apikey", "secret")
    assert mock_smtp_instance.send_message.call_count == 1
    sent_message = mock_smtp_instance.send_message.call_args[0][0]
    assert sent_message["To"] == "alice@example.com"
    assert sent_message["Subject"] == "Verify your account"


def test_real_send_skips_login_when_no_username_configured():
    fake = _FakeSettings()
    fake.email_delivery_enabled = True
    fake.SMTP_HOST = "smtp.example.com"
    fake.SMTP_USERNAME = ""  # e.g. an open relay / local dev SMTP catcher

    mock_smtp_instance = MagicMock()
    mock_smtp_instance.__enter__.return_value = mock_smtp_instance
    mock_smtp_instance.__exit__.return_value = False

    with patch("app.utils.email.settings", fake), \
         patch("app.utils.email.smtplib.SMTP", return_value=mock_smtp_instance):
        send_email("alice@example.com", "Subject", "body")

    mock_smtp_instance.login.assert_not_called()


def test_smtp_failure_raises_email_delivery_error_and_does_not_leak_details():
    fake = _FakeSettings()
    fake.email_delivery_enabled = True
    fake.SMTP_HOST = "smtp.example.com"

    with patch("app.utils.email.settings", fake), \
         patch("app.utils.email.smtplib.SMTP", side_effect=OSError("connection refused")):
        with pytest.raises(EmailDeliveryError) as exc_info:
            send_email("alice@example.com", "Subject", "body")

    assert "connection refused" not in str(exc_info.value)
    assert exc_info.value.status_code == 502


def test_registration_otp_template_contains_code_and_expiry():
    subject, text_body, html_body = render_registration_otp_email("482913", 10)
    assert "482913" in subject
    assert "482913" in text_body
    assert "482913" in html_body
    assert "10 minutes" in text_body


def test_password_reset_template_contains_url():
    url = "https://laptopsathi.ai/reset-password?token=abc123"
    subject, text_body, html_body = render_password_reset_email(url)
    assert url in text_body
    assert url in html_body
    assert "reset" in subject.lower()
