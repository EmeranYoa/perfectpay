import os
from pydantic_settings import BaseSettings
from fastapi.security.api_key import APIKeyHeader
from fastapi_babel import Babel, BabelConfigs

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    APP_ENV: str
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

    STRIPE_PUBLIC_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_ENDPOINT_SECRET: str

    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    STATIC_FOLDER: str

    CYBERSOURCE_MERCHANT_ID: str
    CYBERSOURCE_RUN_ENVIRONMENT: str
    CYBERSOURCE_MERCHANT_KEY: str
    CYBERSOURCE_MERCHANT_SECRETKEY: str
    CYBERSOURCE_WEBHOOK_SECRET: str

    class Config:
        env_file = f"{base_dir}/.env"

settings = Settings()

api_key_header = APIKeyHeader(name="X-API-KEY")

babel_configs = BabelConfigs(
    ROOT_DIR=base_dir+"/app",
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="langs",
)

babel = Babel(babel_configs)
