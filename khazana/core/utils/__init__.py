# flake8: noqa
"""Common utils."""

from .auth_config import (
    create_access_token,
    get_current_user,
    get_current_user_first_login,
    is_weak_password,
    get_password_hash,
    verify_password,
    is_admin,
)
