"""
End-to-end tests for registration email-OTP verification, exercised through
the real HTTP API (FastAPI TestClient) against an isolated SQLite database
— see conftest.py.

Since no SMTP server is configured in tests, app.utils.email.send_email()
falls back to logging a placeholder instead of actually sending — tests
recover the OTP from that log record rather than reading it out of the
database (which only stores a hash).

Run:
    pip install -r requirements.txt -r requirements-dev.txt
    python -m pytest tests/test_registration_otp.py -v
"""
import logging
import re

import pytest

EMAIL = "alice@example.com"
PASSWORD = "StrongPass1"


def _extract_otp(caplog) -> str:
    for record in caplog.records:
        match = re.search(r"verification code is:?\s*(\d{4,8})", record.getMessage())
        if match:
            return match.group(1)
    raise AssertionError("No OTP found in logs — did the placeholder email log fire?")


def _register(client, caplog, email=EMAIL, password=PASSWORD, full_name="Alice"):
    with caplog.at_level(logging.INFO):
        res = client.post("/api/auth/register", json={"email": email, "password": password, "full_name": full_name})
    assert res.status_code == 201, res.text
    otp = _extract_otp(caplog)
    caplog.clear()
    return res.json(), otp


def _login(client, email=EMAIL, password=PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password, "remember_me": False})


# ---------------------------------------------------------------------------
# Registration starts unverified and sends an OTP
# ---------------------------------------------------------------------------

def test_register_creates_unverified_account_and_does_not_log_in(client, caplog):
    body, otp = _register(client, caplog)
    assert body["email"] == EMAIL
    assert "message" in body
    assert re.fullmatch(r"\d{6}", otp)

    # No tokens were issued — registration alone does not grant access.
    assert "access_token" not in body


def test_login_before_verifying_is_rejected(client, caplog):
    _register(client, caplog)
    res = _login(client)
    assert res.status_code == 401
    assert "verify your email" in res.json()["error"]["message"].lower()


# ---------------------------------------------------------------------------
# Verifying the OTP
# ---------------------------------------------------------------------------

def test_verify_otp_with_correct_code_activates_account_and_logs_in(client, caplog):
    _, otp = _register(client, caplog)

    res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": otp})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["access_token"] and body["refresh_token"]
    assert body["user"]["is_verified"] is True

    # Now a normal login works too.
    login_res = _login(client)
    assert login_res.status_code == 200
    assert login_res.json()["access_token"]


def test_verify_otp_with_wrong_code_does_not_activate_account(client, caplog):
    _register(client, caplog)
    res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": "000000"})
    assert res.status_code == 400

    # Still can't log in.
    login_res = _login(client)
    assert login_res.status_code == 401


def test_verify_otp_rejects_unknown_email(client):
    res = client.post("/api/auth/register/verify-otp", json={"email": "nobody@example.com", "otp": "123456"})
    assert res.status_code == 400


def test_repeated_wrong_codes_eventually_lock_out(client, caplog):
    _, otp = _register(client, caplog)
    for _ in range(5):
        res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": "000000"})
        assert res.status_code == 400

    # One more attempt (even with the real code) is now locked out.
    res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": otp})
    assert res.status_code == 401
    assert "too many" in res.json()["error"]["message"].lower()


# ---------------------------------------------------------------------------
# Resend
# ---------------------------------------------------------------------------

def test_resend_otp_issues_a_fresh_code_that_invalidates_the_old_one(client, caplog):
    _, old_otp = _register(client, caplog)

    with caplog.at_level(logging.INFO):
        res = client.post("/api/auth/register/resend-otp", json={"email": EMAIL})
    assert res.status_code == 200
    new_otp = _extract_otp(caplog)
    assert new_otp != old_otp

    # The old code no longer works ...
    old_res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": old_otp})
    assert old_res.status_code == 400

    # ... but the new one does.
    new_res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": new_otp})
    assert new_res.status_code == 200, new_res.text


def test_resend_otp_gives_identical_response_for_unknown_email(client):
    """No user enumeration: same response whether or not the email has a
    pending registration."""
    known = client.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD, "full_name": "Alice"})
    assert known.status_code == 201

    res_known = client.post("/api/auth/register/resend-otp", json={"email": EMAIL})
    res_unknown = client.post("/api/auth/register/resend-otp", json={"email": "nobody@example.com"})
    assert res_known.status_code == res_unknown.status_code == 200
    assert res_known.json() == res_unknown.json()


# ---------------------------------------------------------------------------
# Re-registering / conflicts
# ---------------------------------------------------------------------------

def test_registering_again_before_verifying_reissues_a_new_otp(client, caplog):
    _, first_otp = _register(client, caplog)

    body2, second_otp = _register(client, caplog, password="AnotherPass2")
    assert body2["email"] == EMAIL
    assert second_otp != first_otp

    # New password takes effect once verified.
    res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": second_otp})
    assert res.status_code == 200, res.text

    login_res = client.post("/api/auth/login", json={
        "email": EMAIL, "password": "AnotherPass2", "remember_me": False,
    })
    assert login_res.status_code == 200


def test_registering_an_already_verified_email_is_rejected(client, caplog):
    _, otp = _register(client, caplog)
    client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": otp})

    res = client.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD, "full_name": "Alice"})
    assert res.status_code == 400
    assert "already exists" in res.json()["error"]["message"].lower()


def test_register_surfaces_a_clean_error_if_email_delivery_fails(client, monkeypatch):
    """If SMTP is configured but sending genuinely fails, the account is
    still created (so a retry via resend-otp works), but the caller gets a
    clear 502 rather than a raw SMTP exception."""
    from app.utils.exceptions import EmailDeliveryError

    def _boom(*args, **kwargs):
        raise EmailDeliveryError("We couldn't send that email right now. Please try again in a moment.")

    monkeypatch.setattr("app.auth.router.send_email", _boom)

    res = client.post("/api/auth/register", json={"email": EMAIL, "password": PASSWORD, "full_name": "Alice"})
    assert res.status_code == 502
    assert res.json()["error"]["code"] == "EMAIL_DELIVERY_FAILED"


# ---------------------------------------------------------------------------
# Existing auth flows keep working
# ---------------------------------------------------------------------------

def test_refresh_and_me_work_after_verification(client, caplog):
    _, otp = _register(client, caplog)
    verify_res = client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": otp}).json()

    refresh_res = client.post("/api/auth/refresh", json={"refresh_token": verify_res["refresh_token"]})
    assert refresh_res.status_code == 200
    access = refresh_res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me_res.status_code == 200
    assert me_res.json()["is_verified"] is True


def test_admin_login_and_rbac_still_work(client, db_session, caplog):
    from app.auth.security import hash_password
    from app.models.db_models import User, Role

    role = db_session.query(Role).filter_by(name="admin").first()
    admin = User(
        email="admin@example.com", hashed_password=hash_password("AdminPass1"),
        full_name="Admin", role_id=role.id, is_active=True, is_verified=True,
    )
    db_session.add(admin)
    db_session.commit()

    res = client.post("/api/auth/admin-login", json={"email": "admin@example.com", "password": "AdminPass1"})
    assert res.status_code == 200
    access = res.json()["access_token"]

    admin_res = client.get("/api/admin/logs", headers={"Authorization": f"Bearer {access}"})
    assert admin_res.status_code == 200

    # A verified, correctly-authenticated non-admin account is still
    # rejected by the admin-only login endpoint (role check, not just auth).
    _, otp = _register(client, caplog)
    client.post("/api/auth/register/verify-otp", json={"email": EMAIL, "otp": otp})
    non_admin_res = client.post("/api/auth/admin-login", json={"email": EMAIL, "password": PASSWORD})
    assert non_admin_res.status_code == 401
