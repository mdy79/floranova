from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Floranova"
    APP_TITLE: str = "Floranova Artisan Floral Operations & E-Commerce"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "floranova-super-secret-jwt-key-production-grade-2026-botanica"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./floranova.db"
    
    # Floristry Logistics Configuration
    MAX_SLOT_CAPACITY: int = 8  # Maximum orders per delivery time window to prevent florist burnout
    CURRENCY_NAME: str = "تومان"
    DEFAULT_DELIVERY_FEE: int = 75000  # 75,000 Tomans
    FREE_DELIVERY_THRESHOLD: int = 2500000  # Free delivery above 2.5M Tomans
    
    # Store Profile
    STORE_PHONE: str = "021-88990011"
    STORE_ADDRESS_FA: str = "تهران، خیابان ولیعصر، بالاتر از زعفرانیه، پلاک ۱۱۸"
    INSTAGRAM_HANDLE: str = "@floranova.ir"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
