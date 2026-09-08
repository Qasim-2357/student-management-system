import re
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from app.database import get_db
from app.models.models import Student, Teacher, User

_IDENTIFIER_PATTERN = re.compile(r"^(STU|TCH|ADM)-(\d+)$")


def resolve_login_user(db: Session, identifier: str) -> User | None:
    """Resolve a login identifier to the User account that should
    authenticate.

    Accepts institutional identifiers of the form ``STU-0012``,
    ``TCH-0004``, or ``ADM-0001`` (case-insensitive, whitespace-trimmed by
    the caller), derived from the corresponding Student/Teacher profile id
    or, for admins, the User id directly. Falls back to a legacy exact-match
    email lookup for backward compatibility.

    Returns None if nothing matches. Callers must treat a None result
    identically to an incorrect password (a generic authentication failure)
    so that identifier existence is never revealed.
    """
    value = identifier.strip()
    if not value:
        return None

    match = _IDENTIFIER_PATTERN.match(value.upper())
    if match:
        prefix, number = match.groups()
        profile_id = int(number)
        if prefix == "STU":
            student = db.get(Student, profile_id)
            return student.user if student is not None else None
        if prefix == "TCH":
            teacher = db.get(Teacher, profile_id)
            return teacher.user if teacher is not None else None
        # prefix == "ADM": no separate Admin profile table exists, so the
        # identifier maps directly to a User id, scoped to the admin role.
        user = db.get(User, profile_id)
        return user if user is not None and user.role == "admin" else None

    # Legacy/back-compat path: treat the value as an email address.
    return db.scalar(select(User).where(User.email == value))


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not access_token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            access_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, TypeError, ValueError):
        raise credentials_exception
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user


def require_role(role: str):
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_dependency


get_current_admin = require_role("admin")
get_current_teacher = require_role("teacher")
get_current_student = require_role("student")