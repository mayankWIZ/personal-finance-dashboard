"""User related Endpoints."""

from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from khazana.core.utils import (
    get_current_user,
    get_password_hash,
    get_current_user_first_login,
    verify_password,
    is_weak_password,
    is_admin,
)
from khazana.core.models import UserDB
from khazana.core.serializers import UserOut, UserIn, ChangePasswordIn
from khazana.core.database import get_db
from typing import List


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", description="Get list of users.", response_model=List[UserOut])
async def get_users(
    user: UserDB = Security(get_current_user, scopes=["me"]),
    db: Session = Depends(get_db),
) -> List[UserOut]:
    """List users."""
    filters = [
        UserDB.username.notin_(["admin", user.username])
    ]
    if not is_admin(user):
        filters.append(UserDB.createdBy == user.id)
    return [
        UserOut(**user.__dict__)
        for user in db.query(UserDB).filter(*filters)
    ]


@router.post(
    "",
    description="Create new user.",
    response_model=UserOut,
)
async def post_user(
    user: UserIn,
    loggedin_user: UserDB = Security(get_current_user, scopes=["me"]),
    db: Session = Depends(get_db),
) -> UserOut:
    """Create new user."""
    final_scopes = set(user.scopes)
    if not is_admin(loggedin_user):
        user_scopes = set(loggedin_user.scopes.split(","))
        if final_scopes.difference(user_scopes):
            raise HTTPException(
                403,
                "You can not provide scopes that you "
                "don't have. Please contact admin."
            )
    user = UserDB(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        scopes=",".join(user.scopes),
        firstLogin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(**user.__dict__)


@router.patch(
    "/change_password",
    description="Change password on first login.",
)
async def change_password(
    password_change: ChangePasswordIn,
    user: UserDB = Security(get_current_user_first_login, scopes=["me"]),
    db: Session = Depends(get_db),
) -> UserOut:
    """Change password on first login."""

    if not verify_password(password_change.oldPassword, user.hashed_password):
        raise HTTPException(400, "Incorrect password.")
    if is_weak_password(password_change.newPassword):
        raise HTTPException(
            400,
            "Password is too weak. Password should "
            "include at least 1 uppercase, "
            "1 lowercase, 1 number and "
            "1 special character."
         )
    user = db.get(UserDB, user.id)
    if user.firstLogin:
        user.firstLogin = False
    user.hashed_password = get_password_hash(password_change.newPassword)
    user.emailAddress = password_change.emailAddress
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(**user.__dict__)
