"""Модели базы данных."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Item(Base):
    """Артефакт."""
    __tablename__ = "items"
    
    id = Column(String, primary_key=True)
    name_ru = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    category = Column(String, nullable=False)
    icon = Column(String)


class ItemStats(Base):
    """Статистика артефакта."""
    __tablename__ = "item_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    region = Column(String, nullable=False)
    quality = Column(String, default="")
    upgrade_level = Column(Integer, default=0)
    
    market_price = Column(Float, nullable=True)
    median = Column(Float, nullable=True)
    mean = Column(Float, nullable=True)
    mode = Column(Float, nullable=True)
    lowest_lot = Column(Float, nullable=True)
    active_lots = Column(Integer, default=0)
    liquidity = Column(Float, default=0.0)
    volatility = Column(Float, default=0.0)
    spread = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    change_24h = Column(Float, default=0.0)
    change_7d = Column(Float, default=0.0)
    sales_24h = Column(Integer, default=0)
    sample_size = Column(Integer, default=0)
    computed_at = Column(DateTime, default=datetime.utcnow)


class LotSnapshot(Base):
    """Снимок лота."""
    __tablename__ = "lot_snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    region = Column(String, nullable=False)
    lot_key = Column(String, nullable=False)
    
    price = Column(Float, nullable=False)
    amount = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    quality = Column(String, default="")
    upgrade_level = Column(Integer, default=0)
    
    ends_at = Column(DateTime, nullable=True)
    seen_at = Column(DateTime, default=datetime.utcnow)
    first_seen_at = Column(DateTime, nullable=True)
    gone_at = Column(DateTime, nullable=True)
    missing_streak = Column(Integer, default=0)


class Sale(Base):
    """Продажа."""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    region = Column(String, nullable=False)
    
    price = Column(Float, nullable=False)
    amount = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    quality = Column(String, default="")
    upgrade_level = Column(Integer, default=0)
    sold_at = Column(DateTime, default=datetime.utcnow)


class MarketEvent(Base):
    """Событие на рынке."""
    __tablename__ = "market_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    region = Column(String, nullable=False)
    
    type = Column(String, nullable=False)
    magnitude = Column(Float, default=0.0)
    message = Column(Text, default="")
    happened_at = Column(DateTime, default=datetime.utcnow)
