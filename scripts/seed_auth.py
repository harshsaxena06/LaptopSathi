"""
Seeds the `roles` and `permissions` tables (and links them), and optionally
creates the first admin user. Idempotent — safe to re-run.

Run:
    python scripts/seed_auth.py
    python scripts/seed_auth.py --admin-email admin@laptopsathi.ai --admin-password "ChangeMe123!"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db
from app.models.db_models import Role, Permission, User
from app.auth.security import hash_password

USER_PERMISSIONS = [
    ("search:laptops", "Search the laptop knowledge base"),
    ("recommend:get", "Get AI recommendations"),
    ("compare:laptops", "Compare laptops"),
    ("wishlist:manage", "Save/unsave laptops"),
    ("profile:manage", "View/edit own profile"),
    ("preferences:manage", "View/edit own preferences"),
]

ADMIN_ONLY_PERMISSIONS = [
    ("kb:upload", "Upload a new knowledge-base dataset"),
    ("kb:version", "View/rollback knowledge-base versions"),
    ("analytics:view", "View the analytics dashboard"),
    ("users:manage", "Manage user accounts and roles"),
    ("settings:manage", "View/change system settings"),
    ("logs:view", "View system logs"),
]


def upsert_permission(db, code: str, description: str) -> Permission:
    perm = db.query(Permission).filter_by(code=code).first()
    if perm is None:
        perm = Permission(code=code, description=description)
        db.add(perm)
        db.flush()
    return perm


def upsert_role(db, name: str, description: str, permission_codes: list[str]) -> Role:
    role = db.query(Role).filter_by(name=name).first()
    if role is None:
        role = Role(name=name, description=description)
        db.add(role)
        db.flush()
    role.permissions = [upsert_permission(db, code, "") for code in permission_codes]
    return role


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--admin-email", default=None)
    parser.add_argument("--admin-password", default=None)
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        all_perm_codes = [c for c, _ in USER_PERMISSIONS]
        admin_perm_codes = all_perm_codes + [c for c, _ in ADMIN_ONLY_PERMISSIONS]

        for code, desc in USER_PERMISSIONS + ADMIN_ONLY_PERMISSIONS:
            upsert_permission(db, code, desc)

        upsert_role(db, "user", "Standard end user", all_perm_codes)
        admin_role = upsert_role(db, "admin", "Administrator — full access", admin_perm_codes)
        db.commit()
        print("Seeded roles: user, admin")
        print(f"Seeded {len(USER_PERMISSIONS) + len(ADMIN_ONLY_PERMISSIONS)} permissions")

        if args.admin_email and args.admin_password:
            existing = db.query(User).filter_by(email=args.admin_email.lower()).first()
            if existing:
                print(f"Admin user {args.admin_email} already exists — skipping creation.")
            else:
                admin_user = User(
                    email=args.admin_email.lower(),
                    hashed_password=hash_password(args.admin_password),
                    full_name="Administrator",
                    role_id=admin_role.id,
                    is_active=True,
                    is_verified=True,
                )
                db.add(admin_user)
                db.commit()
                print(f"Created admin user: {args.admin_email}")
        else:
            print("No --admin-email/--admin-password given — skipped creating an admin user.")
            print("Create one later via the API, or re-run with those flags.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
