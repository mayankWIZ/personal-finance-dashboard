# flake8: noqa
"""Common utils."""

from .auth_config import (
    create_access_token,
    get_current_user,
    get_current_user_first_login,
    get_password_hash,
    is_admin,
    is_weak_password,
    verify_password,
)
