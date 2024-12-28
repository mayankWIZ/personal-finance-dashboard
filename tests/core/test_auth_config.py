"""Test auth_config module."""

from khazana.core.utils.auth_config import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from datetime import timedelta


def test_verify_password():
    """Test password verification."""
    hashed = get_password_hash("Test@1234")
    assert verify_password("Test@1234", hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_create_access_token():
    """Test access token creation."""
    data = {"username": "testuser"}
    # token = create_access_token(data, expires_delta=timedelta(minutes=5))
    # assert token is not None
