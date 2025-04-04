import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Bot Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "credentials/firebase_service_account.json")
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "https://sihp-2135d-default-rtdb.firebaseio.com/")
    
    # Model settings
    MOUSE_MODEL_PATH: str = os.getenv("MOUSE_MODEL_PATH", "models/MouseVerifier.pkl")
    KEYBOARD_MODEL_PATH: str = os.getenv("KEYBOARD_MODEL_PATH", "models/KeyboardVerifier.pkl")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """Get cached settings"""
    return Settings()