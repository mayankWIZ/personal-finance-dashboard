"""User utils."""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.users import UserDB


def is_exising_user(user: dict, db: Session) -> bool:
    """Check if user exists."""
    return True if (db.query(UserDB).filter(
        or_(
            UserDB.username == user["username"],
            UserDB.emailAddress == user["emailAddress"],
        )
    ).first()) else False
