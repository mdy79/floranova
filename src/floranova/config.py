from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Floli Flowers"
    APP_TITLE: str = "گلِفِلـولی• | Floli Flowers"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "floli-flowers-super-secret-jwt-key-production-grade-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./floranova.db"
    
    # Floristry Logistics Configuration
    MAX_SLOT_CAPACITY: int = 8  # Maximum orders per delivery time window to prevent florist burnout
    CURRENCY_NAME: str = "تومان"
    DEFAULT_DELIVERY_FEE: int = 75000  # 75,000 Tomans
    FREE_DELIVERY_THRESHOLD: int = 2500000  # Free delivery above 2.5M Tomans
    
    # Store Profile (from https://www.instagram.com/floli.flowers)
    STORE_NAME_FA: str = "گلِفِلـولی•"
    STORE_SLOGAN_FA: str = "فِلـولی | برایِ لحـظههایِ ماندگار"
    STORE_PHONE: str = "09304242180"
    STORE_PHONE_FA: str = "۰۹۳۰۴۲۴۲۱۸۰"
    STORE_ADDRESS_FA: str = "تهران و کرج (ارسال تشریفاتی و تحویل حضوری استودیو)"
    STORE_CITIES_FA: str = "تهران و کرج"
    INSTAGRAM_HANDLE: str = "floli.flowers"
    INSTAGRAM_URL: str = "https://www.instagram.com/floli.flowers"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
