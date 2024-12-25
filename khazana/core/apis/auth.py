from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from khazana.core.models import UserDB
from khazana.core.serializers import OAuth2PasswordRequestForm
from khazana.core.utils import (
    create_access_token,
    is_weak_password,
    verify_password
)
from khazana.core.database import get_db

router = APIRouter()


@router.post(
    "/auth",
    tags=["Authentication"],
    description="Get authentication token.",
)
def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Get authentication token."""
    password_policy_violation = False
    if form_data.username and form_data.password:
        user: UserDB = db.query(UserDB).filter(
            UserDB.username == form_data.username
        ).first()
        if not user:
            raise HTTPException(401, "Incorrect username or password.")

        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(401, "Incorrect username or password.")
        password_policy_violation = is_weak_password(form_data.password)
    else:
        raise HTTPException(401, "Incorrect username or password.")
    if form_data.scopes:  # verify scopes if any
        for scope in form_data.scopes:
            if scope not in user.scopes.split(","):
                raise HTTPException(403, "Unauthorized")
        granted_scopes = form_data.scopes
    else:
        # if no scopes specified; grant all of allowed scopes
        granted_scopes = user.scopes.split(",")
    token = create_access_token(
        {"username": user.username, "scopes": granted_scopes}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "scopes": granted_scopes,
        "firstLogin": user.firstLogin,
        "passwordPolicyViolation": password_policy_violation,
    }
