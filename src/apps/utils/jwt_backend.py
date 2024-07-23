# Third-Party
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy,
)
from fastapi_users import FastAPIUsers

# Local
from src.settings.const import JWT_KEY
from src.apps.models.users import User
from .manager import get_user_manager


bearer_transport = BearerTransport(tokenUrl="auth/login/")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=JWT_KEY, lifetime_seconds=60*60*6)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager, [auth_backend]
)
current_user = fastapi_users.current_user()
