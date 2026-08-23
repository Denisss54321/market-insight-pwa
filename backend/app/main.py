"""Главный файл backend приложения."""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import init_db
from app.collector import StalcraftCollector
from app.websocket import manager
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация базы данных
    init_db()
    
    # Запуск коллектора
    collector = StalcraftCollector()
    collector_task = asyncio.create_task(collector.run())
    
    logger.info("Backend запущен")
    
    try:
        yield
    finally:
        collector.running = False
        collector_task.cancel()
        try:
            await collector_task
        except asyncio.CancelledError:
            pass
        logger.info("Backend остановлен")


app = FastAPI(
    title="Market Insight PWA Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "status": "ok",
        "service": "Market Insight PWA Backend",
        "region": settings.region,
        "active_connections": len(manager.active_connections)
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time данных."""
    await manager.connect(websocket)
    try:
        while True:
            # Получаем сообщения от клиента (ping/pong)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
