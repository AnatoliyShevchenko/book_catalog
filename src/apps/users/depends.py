# Third-Party
from fastapi_users.authentication import Authenticator

# Local
from src.apps.abstract.jwt_backend import auth_backend
from .manager import get_user_manager
from .models import User


def get_current_user_token():
    authenticator = Authenticator(
        backends=[auth_backend], get_user_manager=get_user_manager()
    )
    authenticator.current_user_token(
        active=True, verified=False
    )

