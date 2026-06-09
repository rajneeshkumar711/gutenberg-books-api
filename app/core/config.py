from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # No default — must be set via .env file or environment variable.
    # Example: DATABASE_URL=postgresql://user:pass@host:5432/dbname
    DATABASE_URL: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
