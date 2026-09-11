from typing import Optional
from fastapi import Header
from sqlalchemy.orm import Session
from app.models.user import User


def get_current_user_id(
    x_user_id: Optional[int] = Header(
        None,
        alias="X-User-Id",
        description="Development-only user identifier. Defaults to 1 if omitted. Will be replaced by authentication context in future phases.",
    )
) -> int:
    """
    Explicit ownership boundary dependency.
    In development without authentication, resolves the calling user ID from
    an optional header or defaults to 1. When authentication is added in a
    later phase, only this dependency will be swapped to extract user identity from JWT/session.
    """
    if x_user_id is not None and x_user_id > 0:
        return x_user_id
    return 1


def ensure_dev_user(db: Session, user_id: int = 1) -> User:
    """
    Ensures a default developer user exists in the database to satisfy foreign keys.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            email="developer@mindos.local",
            name="Development User",
            timezone="UTC",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
