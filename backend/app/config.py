from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ARCDIS Backend"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "change_me_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "arcdis_db"

    class Config:
        env_file = ".env"

settings = Settings()
