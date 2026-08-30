import os

from dotenv import load_dotenv

load_dotenv()

_PLACEHOLDER_SECRETS = {
    "",
    "change-this-to-a-long-random-secret-key",
    "change-me",
    "your-secret-key",
    "development-only-secret-change-me",
}
_DEVELOPMENT_SECRET = "development-only-secret-change-me"


def is_production() -> bool:
    return os.getenv("APP_ENV", "development").strip().lower() in {
        "production",
        "prod",
    }


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        return database_url
    raise RuntimeError("DATABASE_URL must be set")


def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if is_production() and secret.lower() in _PLACEHOLDER_SECRETS:
        raise RuntimeError(
            "JWT_SECRET_KEY must be set to a non-placeholder value in production"
        )
    return secret or _DEVELOPMENT_SECRET


def validate_configuration() -> None:
    get_database_url()
    get_jwt_secret()


DATABASE_URL = get_database_url()
JWT_SECRET_KEY = get_jwt_secret()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
