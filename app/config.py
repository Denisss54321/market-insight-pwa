"""Конфигурация backend."""

from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # API Stalcraft
    stalcraft_api_base: str = "https://eapi.stalcraft.net"
    stalcraft_client_id: str = ""
    stalcraft_client_secret: str = ""
    stalcraft_api_token: str = ""
    
    # Регион
    region: str = "RU"
    
    # Лимиты API
    requests_per_minute: int = 45
    request_timeout: float = 10.0
    
    # Интервалы сканирования
    hot_interval_seconds: float = 45.0
    warm_interval_seconds: float = 300.0
    cold_interval_seconds: float = 3600.0
    
    # Количество артефактов
    hot_items: int = 20
    warm_items: int = 40
    
    # База данных
    database_url: str = "postgresql://user:password@localhost/market_insight"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # WebSocket
    ws_max_connections: int = 1000
    
    class Config:
        env_prefix = "MI_"
        env_file = ".env"


settings = Settings()
