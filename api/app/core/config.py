from pydantic_settings import BaseSettings
from decouple import config


class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"

    JWT_SECRET_KEY                      : str = config('JWT_SECRET_KEY', cast=str)

    DB_USER                             : str = config('DB_USER', cast=str)
    DB_PASS                             : str = config('DB_PASS', cast=str)
    DB_NAME                             : str = config('DB_NAME', cast=str)
    DB_HOST                             : str = config('DB_HOST', cast=str)
    DB_PORT                             : str = config('DB_PORT', cast=int)

    class Config:
        env_file = ".env"

settings = Settings()