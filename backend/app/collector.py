"""Коллектор данных из Stalcraft API."""

import asyncio
import httpx
import random
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.config import settings
from app.db import get_db
from app.models import Item, ItemStats, LotSnapshot, Sale

logger = logging.getLogger(__name__)


class StalcraftCollector:
    """Коллектор данных из Stalcraft API."""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.running = False
        self.last_request_time = datetime.min
        self.request_count = 0
        
    async def start(self):
        """Запуск коллектора."""
        self.client = httpx.AsyncClient(timeout=settings.request_timeout)
        self.running = True
        logger.info("Коллектор запущен")
        
    async def stop(self):
        """Остановка коллектора."""
        self.running = False
        if self.client:
            await self.client.aclose()
        logger.info("Коллектор остановлен")
        
    async def _rate_limit(self):
        """Ограничение частоты запросов."""
        now = datetime.utcnow()
        if now - self.last_request_time < timedelta(minutes=1):
            if self.request_count >= settings.requests_per_minute:
                wait_time = 60 - (now - self.last_request_time).total_seconds()
                if wait_time > 0:
                    logger.info(f"Rate limit: ждем {wait_time:.1f} сек")
                    await asyncio.sleep(wait_time)
                    self.request_count = 0
                    self.last_request_time = datetime.utcnow()
        self.request_count += 1
        
    async def fetch_items(self) -> list[dict]:
        """Получение списка артефактов."""
        await self._rate_limit()
        
        headers = {}
        if settings.stalcraft_api_token:
            headers["Authorization"] = f"Bearer {settings.stalcraft_api_token}"
        elif settings.stalcraft_client_id and settings.stalcraft_client_secret:
            # Получение токена через OAuth
            pass
            
        response = await self.client.get(
            f"{settings.stalcraft_api_base}/{settings.region}/items",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
        
    async def fetch_market_lots(self, item_id: str) -> list[dict]:
        """Получение лотов на рынке."""
        await self._rate_limit()
        
        headers = {}
        if settings.stalcraft_api_token:
            headers["Authorization"] = f"Bearer {settings.stalcraft_api_token}"
            
        response = await self.client.get(
            f"{settings.stalcraft_api_base}/{settings.region}/market/{item_id}/lots",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
        
    async def fetch_market_history(self, item_id: str, days: int = 7) -> list[dict]:
        """Получение истории продаж."""
        await self._rate_limit()
        
        headers = {}
        if settings.stalcraft_api_token:
            headers["Authorization"] = f"Bearer {settings.stalcraft_api_token}"
            
        response = await self.client.get(
            f"{settings.stalcraft_api_base}/{settings.region}/market/{item_id}/history",
            headers=headers,
            params={"days": days}
        )
        response.raise_for_status()
        return response.json()
        
    async def collect_hot_items(self):
        """Сбор данных для горячих артефактов."""
        with get_db() as db:
            # Получаем горячие артефакты (высшая ликвидность)
            hot_items = db.query(ItemStats).order_by(
                ItemStats.liquidity.desc()
            ).limit(settings.hot_items).all()
            
            # Если нет данных, создаем mock данные для тестирования
            if not hot_items:
                await self._create_mock_data(db)
                hot_items = db.query(ItemStats).order_by(
                    ItemStats.liquidity.desc()
                ).limit(settings.hot_items).all()
            
            for item_stat in hot_items:
                try:
                    # Если нет API ключей, используем mock данные
                    if not settings.stalcraft_api_token:
                        await self._create_mock_lots(db, item_stat.item_id)
                    else:
                        lots = await self.fetch_market_lots(item_stat.item_id)
                        await self._process_lots(db, item_stat.item_id, lots)
                        
                        history = await self.fetch_market_history(item_stat.item_id)
                        await self._process_history(db, item_stat.item_id, history)
                    
                    await self._update_stats(db, item_stat.item_id)
                    
                except Exception as e:
                    logger.error(f"Ошибка при сборе {item_stat.item_id}: {e}")
                    # При ошибке используем mock данные
                    await self._create_mock_lots(db, item_stat.item_id)
                    
    async def _process_lots(self, db, item_id: str, lots: list[dict]):
        """Обработка лотов."""
        from app.websocket import manager
        
        for lot in lots:
            # Проверяем существование лота
            existing = db.query(LotSnapshot).filter_by(
                lot_key=lot.get("lot_key"),
                item_id=item_id
            ).first()
            
            if existing:
                # Обновляем существующий лот
                existing.price = lot.get("price")
                existing.amount = lot.get("amount")
                existing.unit_price = lot.get("unit_price")
                existing.ends_at = lot.get("ends_at")
                existing.seen_at = datetime.utcnow()
                existing.missing_streak = 0
                
                # Отправляем обновление через WebSocket
                await manager.send_lot_update(item_id, {
                    "lot_key": existing.lot_key,
                    "price": existing.price,
                    "amount": existing.amount,
                    "unit_price": existing.unit_price
                })
            else:
                # Создаем новый лот
                new_lot = LotSnapshot(
                    item_id=item_id,
                    region=settings.region,
                    lot_key=lot.get("lot_key"),
                    price=lot.get("price"),
                    amount=lot.get("amount"),
                    unit_price=lot.get("unit_price"),
                    ends_at=lot.get("ends_at"),
                    seen_at=datetime.utcnow()
                )
                db.add(new_lot)
                
    async def _process_history(self, db, item_id: str, history: list[dict]):
        """Обработка истории продаж."""
        from app.websocket import manager
        
        for sale in history:
            existing = db.query(Sale).filter_by(
                item_id=item_id,
                sold_at=sale.get("sold_at")
            ).first()
            
            if not existing:
                new_sale = Sale(
                    item_id=item_id,
                    region=settings.region,
                    price=sale.get("price"),
                    amount=sale.get("amount"),
                    unit_price=sale.get("unit_price"),
                    sold_at=sale.get("sold_at")
                )
                db.add(new_sale)
                
                # Отправляем обновление через WebSocket
                await manager.send_sale_update(item_id, {
                    "price": new_sale.price,
                    "amount": new_sale.amount,
                    "unit_price": new_sale.unit_price,
                    "sold_at": new_sale.sold_at.isoformat()
                })
                
    async def _update_stats(self, db, item_id: str):
        """Обновление статистики."""
        from app.websocket import manager
        
        # Получаем последние продажи
        since = datetime.utcnow() - timedelta(hours=24)
        recent_sales = db.query(Sale).filter(
            Sale.item_id == item_id,
            Sale.sold_at >= since
        ).all()
        
        if recent_sales:
            prices = [s.unit_price for s in recent_sales]
            stats = db.query(ItemStats).filter_by(
                item_id=item_id,
                region=settings.region
            ).first()
            
            if stats:
                stats.market_price = prices[0]  # Последняя цена
                stats.sales_24h = len(recent_sales)
                stats.sample_size = len(prices)
                stats.computed_at = datetime.utcnow()
                
                # Отправляем обновление через WebSocket
                await manager.send_stats_update(item_id, {
                    "market_price": stats.market_price,
                    "sales_24h": stats.sales_24h,
                    "liquidity": stats.liquidity
                })
    
    async def _create_mock_data(self, db):
        """Создание mock данных для тестирования."""
        from app.models import Item, ItemStats
        
        # Создаем mock артефакты
        mock_items = [
            Item(id="artifact_1", name_ru="Кристалл", name_en="Crystal", category="Ресурсы"),
            Item(id="artifact_2", name_ru="Камень", name_en="Stone", category="Ресурсы"),
            Item(id="artifact_3", name_ru="Металл", name_en="Metal", category="Ресурсы"),
        ]
        
        for item in mock_items:
            existing = db.query(Item).filter_by(id=item.id).first()
            if not existing:
                db.add(item)
        
        db.commit()
        
        # Создаем mock статистику
        for item in mock_items:
            existing = db.query(ItemStats).filter_by(
                item_id=item.id,
                region=settings.region
            ).first()
            if not existing:
                stats = ItemStats(
                    item_id=item.id,
                    region=settings.region,
                    market_price=100.0 + hash(item.id) % 50,
                    liquidity=0.8 + (hash(item.id) % 20) / 100,
                    sales_24h=10 + hash(item.id) % 20,
                    active_lots=5 + hash(item.id) % 10,
                    computed_at=datetime.utcnow()
                )
                db.add(stats)
        
        db.commit()
        logger.info("Mock данные созданы")
    
    async def _create_mock_lots(self, db, item_id: str):
        """Создание mock лотов для тестирования."""
        # Создаем mock лоты
        for i in range(5):
            lot_key = f"mock_lot_{item_id}_{i}"
            existing = db.query(LotSnapshot).filter_by(
                lot_key=lot_key,
                item_id=item_id
            ).first()
            
            if not existing:
                price = 100.0 + random.random() * 50
                new_lot = LotSnapshot(
                    item_id=item_id,
                    region=settings.region,
                    lot_key=lot_key,
                    price=price,
                    amount=random.randint(1, 10),
                    unit_price=price / random.randint(1, 10),
                    seen_at=datetime.utcnow()
                )
                db.add(new_lot)
        
        db.commit()
        logger.info(f"Mock лоты созданы для {item_id}")
                
    async def run(self):
        """Главный цикл коллектора."""
        await self.start()
        
        while self.running:
            try:
                await self.collect_hot_items()
                logger.info("Сбор данных завершен")
                await asyncio.sleep(settings.hot_interval_seconds)
                
            except Exception as e:
                logger.error(f"Ошибка в главном цикле: {e}")
                await asyncio.sleep(60)
