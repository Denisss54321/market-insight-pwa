"""Конфигурация backend."""

from pydantic import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # API Stalcraft
    stalcraft_api_base: str = os.getenv("MI_STALCRAFT_API_BASE", "https://eapi.stalcraft.net")
    stalcraft_client_id: str = os.getenv("MI_STALCRAFT_CLIENT_ID", "")
    stalcraft_client_secret: str = os.getenv("MI_STALCRAFT_CLIENT_SECRET", "")
    stalcraft_api_token: str = os.getenv("MI_STALCRAFT_API_TOKEN", "")
    
    # Регион
    region: str = os.getenv("MI_REGION", "RU")
    
    # Лимиты API
    requests_per_minute: int = int(os.getenv("MI_REQUESTS_PER_MINUTE", "45"))
    request_timeout: float = float(os.getenv("MI_REQUEST_TIMEOUT", "10.0"))
    
    # Интервалы сканирования
    hot_interval_seconds: float = float(os.getenv("MI_HOT_INTERVAL_SECONDS", "45.0"))
    warm_interval_seconds: float = float(os.getenv("MI_WARM_INTERVAL_SECONDS", "300.0"))
    cold_interval_seconds: float = float(os.getenv("MI_COLD_INTERVAL_SECONDS", "3600.0"))
    
    # Количество артефактов
    hot_items: int = int(os.getenv("MI_HOT_ITEMS", "20"))
    warm_items: int = int(os.getenv("MI_WARM_ITEMS", "40"))
    
    # База данных
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/market_insight")
    
    # CORS
    cors_origins: str = os.getenv("MI_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    
    # WebSocket
    ws_max_connections: int = int(os.getenv("MI_WS_MAX_CONNECTIONS", "1000"))


settings = Settings()
