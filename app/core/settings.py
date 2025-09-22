import os
from dotenv import load_dotenv

# Load variables from .env into os.environ
load_dotenv()

def _get(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v if v is not None else default

class Settings:
    # App
    app_name: str = _get("APP_NAME", "Chat Platform")

    # Auth
    jwt_secret: str = _get("JWT_SECRET", "change-me")
    jwt_alg: str = _get("JWT_ALG", "HS256")
    jwt_expire_min: int = int(_get("JWT_EXPIRE_MIN", "60"))

    # DB
    database_url: str = _get("DATABASE_URL", "sqlite:///./chat.db")

    # Providers
    openai_api_key: str | None = _get("OPENAI_API_KEY")
    openai_model: str = _get("OPENAI_MODEL", "gpt-4o-mini")

    openrouter_api_key: str | None = _get("OPENROUTER_API_KEY")
    openrouter_model: str | None = _get("OPENROUTER_MODEL")

    groq_api_key: str | None = _get("GROQ_API_KEY")

settings = Settings()
