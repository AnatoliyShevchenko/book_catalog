# Third-Party
from decouple import config

# JWT
JWT_KEY = config("JWT_KEY")

# Postgres
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
DB_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Local
VOLUME = "./volume/"

# Celery
CELERY_BROKER_URL = config("CELERY_BROKER_URL")
