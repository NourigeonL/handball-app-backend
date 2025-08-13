
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):

    GOOGLE_AUTH_CLIENT_ID: str = ""
    GOOGLE_AUTH_CLIENT_SECRET: str = ""
    BASE_URL: str = "http://localhost:8000"
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_TIME: int = 3600

settings = Settings()

print(settings)