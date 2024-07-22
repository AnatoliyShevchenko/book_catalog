# Third-Party
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy,
)

# Local
from src.settings.const import JWT_KEY


bearer_transport = BearerTransport(tokenUrl="auth/login/")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=JWT_KEY, lifetime_seconds=60*60*6)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
