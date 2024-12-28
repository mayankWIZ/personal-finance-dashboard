"""User related Endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from khazana.core.database import get_db
from khazana.core.models import UserDB
from khazana.core.serializers import (
    ChangePasswordIn,
    UserIn,
    UserOut,
    UserUpdate,
    UserSignupIn,
)
from khazana.core.utils import (
    get_current_user,
    get_current_user_first_login,
    get_password_hash,
    is_admin,
    is_exising_user,
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
        UserOut(**user.__dict__)
        for user in db.query(UserDB).filter(*filters, UserDB.active == True).all()
    ]


@router.get(
    "/me",
    description="Get user by username.",
    response_model=UserOut,
)
async def get_me(
    user: UserDB = Security(get_current_user, scopes=["me"]),
    db: Session = Depends(get_db),
) -> UserOut:
    """Get user by username."""
    return UserOut(**user.__dict__)


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
    if is_exising_user(
        {"username": user.username, "emailAddress": user.emailAddress}, db
    ):
        raise HTTPException(400, "User with same username or email already exists.")
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
        fullName=user.fullName,
        emailAddress=user.emailAddress,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        scopes=",".join(user.scopes),
        firstLogin=True,
        createdBy=loggedin_user.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(**user.__dict__)


@router.post(
    "/signup",
    description="Signup as a new user.",
    response_model=UserOut,
)
async def signup_new_user(
    user: UserSignupIn,
    db: Session = Depends(get_db),
) -> UserOut:
    """Create new user."""
    if is_exising_user(
        {"username": user.username, "emailAddress": user.emailAddress}, db
    ):
        raise HTTPException(400, "User with same username or email already exists.")
    user = UserDB(
        fullName=user.fullName,
        emailAddress=user.emailAddress,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        scopes=",".join(["me"]),
        firstLogin=False,
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
        db.query(UserDB).filter(UserDB.username == user_update.username).first()
    )
    if not user_requested:
        raise HTTPException(status_code=404, detail="User not found")
    user_update = user_update.model_dump(exclude_none=True)
    for key, value in user_update.items():
        if key == "scopes":
            value = ",".join(value)
        setattr(user_requested, key, value)
    db.add(user_requested)
    db.commit()
    db.refresh(user_requested)
    return UserOut(**user_requested.__dict__)


@router.delete("", description="Delete user.")
async def delete_user(
    username: str,
    user: UserDB = Security(get_current_user, scopes=["admin"]),
    db: Session = Depends(get_db),
):
    """Delete user."""
    if username == "admin":
        raise HTTPException(403, "You can not delete admin.")
    user = (
        db.query(UserDB)
        .filter(UserDB.username == username, UserDB.active == True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.active = False
    db.commit()
    db.refresh(user)
    return {"success": True}
