import os
from pydantic_settings import BaseSettings

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_VERSION: str
    
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: str
    MYSQL_DATABASE: str

    SMS_ENDPOINT: str
    SMS_API_KEY: str
    SMS_SENDER: str
    SMS_PASSWORD: str

    PAYCOOL_ENPOINT: str
    PAYCOOL_EMAIL: str

    STRIPE_SECRET_KEY: str

    class Config:
        env_file = f"{base_dir}/.env"

settings = Settings()