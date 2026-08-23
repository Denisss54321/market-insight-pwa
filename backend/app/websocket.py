"""WebSocket сервер для real-time данных."""

import json
import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Менеджер WebSocket соединений."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """Подключение клиента."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Клиент подключен. Всего: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Отключение клиента."""
        self.active_connections.discard(websocket)
        logger.info(f"Клиент отключен. Всего: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Отправка сообщения всем клиентам."""
        if not self.active_connections:
            return
            
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Ошибка отправки: {e}")
                disconnected.add(connection)
        
        # Удаляем отключенные соединения
        for connection in disconnected:
            self.disconnect(connection)
            
    async def send_lot_update(self, item_id: str, lot_data: dict):
        """Отправка обновления лота."""
        message = {
            "type": "lot_update",
            "item_id": item_id,
            "data": lot_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
        
    async def send_sale_update(self, item_id: str, sale_data: dict):
        """Отправка обновления продажи."""
        message = {
            "type": "sale_update",
            "item_id": item_id,
            "data": sale_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
        
    async def send_stats_update(self, item_id: str, stats_data: dict):
        """Отправка обновления статистики."""
        message = {
            "type": "stats_update",
            "item_id": item_id,
            "data": stats_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)


manager = ConnectionManager()
