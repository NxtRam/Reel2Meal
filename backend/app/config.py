from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/reel2meal"
    SECRET_KEY: str = "change_me_to_a_long_random_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Razorpay — get test keys at https://dashboard.razorpay.com → Settings → API Keys
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""


settings = Settings()
