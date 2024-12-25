"""User related Endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from khazana.core.database import get_db
from khazana.core.models import UserDB
from khazana.core.serializers import ChangePasswordIn, UserIn, UserOut, UserUpdate
from khazana.core.utils import (
    get_current_user,
    get_current_user_first_login,
    get_password_hash,
    is_admin,
    is_weak_password,
    verify_password,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", description="Get list of users.", response_model=List[UserOut])
async def get_users(
    user: UserDB = Security(get_current_user, scopes=["me"]),
    db: Session = Depends(get_db),
) -> List[UserOut]:
    """List users."""
    filters = [UserDB.username.notin_(["admin", user.username])]
    if not is_admin(user):
        filters.append(UserDB.createdBy == user.id)
    return [
        UserOut(**user.__dict__) for user in db.query(UserDB).filter(*filters)
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
                "don't have. Please contact admin.",
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
            "1 special character.",
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


@router.patch(
    "",
    description="Update user.",
    response_model=UserOut,
)
async def update_user(
    user_update: UserUpdate,
    user: UserDB = Security(get_current_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> UserOut:
    """Update user."""
    if user_update.username == "admin" and "admin" not in user_update.scopes:
        raise HTTPException(403, "You can not update admin.")

    user_requested = (
        db.query(UserDB)
        .filter(UserDB.username == user_update.username)
        .first()
    )
    if not user_requested:
        raise HTTPException(status_code=404, detail="User not found")
    if user_requested.scopes == ",".join(user_update.scopes):
        return UserOut(**user_requested.__dict__)
    user_requested.scopes = ",".join(user_update.scopes)
    db.add(user_requested)
    db.commit()
    db.refresh(user_requested)
    return UserOut(**user_requested.__dict__)


@router.delete(
    "",
    description="Delete user."
)
async def delete_user(
    username: str,
    user: UserDB = Security(get_current_user, scopes=["admin"]),
    db: Session = Depends(get_db),
) -> UserOut:
    """Delete user."""
    if username == "admin":
        raise HTTPException(403, "You can not delete admin.")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.active = False
    db.commit()
    db.refresh(user)
    return {"success": True}
