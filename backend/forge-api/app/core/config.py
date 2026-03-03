from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./forge.db"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 12
    FERNET_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:4321"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
