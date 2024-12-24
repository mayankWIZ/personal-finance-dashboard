"""Auth serializers."""

from fastapi.param_functions import Form


class OAuth2PasswordRequestForm:
    """Credential request form."""

    def __init__(
        self,
        username: str = Form(None),
        password: str = Form(None),
        scope: str = Form(""),
    ):
        """Initialize."""
        self.username = username
        self.password = password
        self.scopes = scope.split()
