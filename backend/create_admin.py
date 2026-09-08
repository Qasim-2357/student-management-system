import os

from app.database import SessionLocal
from app.models.models import User
from app.security import hash_password


def main() -> None:
    admin_name = os.getenv("ADMIN_NAME", "").strip()
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")

    if not admin_name:
        raise RuntimeError("ADMIN_NAME must be set")

    if not admin_email:
        raise RuntimeError("ADMIN_EMAIL must be set")

    if not admin_password:
        raise RuntimeError("ADMIN_PASSWORD must be set")

    db = SessionLocal()

    try:
        existing_admin = db.query(User).filter(User.email == admin_email).first()

        if existing_admin is not None:
            raise RuntimeError(
                f"A user with email '{admin_email}' already exists"
            )

        admin = User(
            name=admin_name,
            email=admin_email,
            password_hash=hash_password(admin_password),
            role="admin",
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()