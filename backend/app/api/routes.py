"""API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Item, ItemStats, LotSnapshot, Sale
from pydantic import BaseModel

router = APIRouter()


# Schemas
class ItemSchema(BaseModel):
    id: str
    name_ru: str
    name_en: str
    category: str
    icon: str | None = None


class ItemStatsSchema(BaseModel):
    item_id: str
    region: str
    quality: str
    upgrade_level: int
    market_price: float | None
    median: float | None
    mean: float | None
    mode: float | None
    lowest_lot: float | None
    active_lots: int
    liquidity: float
    volatility: float
    spread: float
    confidence: float
    change_24h: float
    change_7d: float
    sales_24h: int
    sample_size: int
    computed_at: str


class LotSnapshotSchema(BaseModel):
    id: int
    item_id: str
    region: str
    lot_key: str
    price: float
    amount: int
    unit_price: float
    quality: str
    upgrade_level: int
    ends_at: str | None
    seen_at: str


class SaleSchema(BaseModel):
    id: int
    item_id: str
    region: str
    price: float
    amount: int
    unit_price: float
    quality: str
    upgrade_level: int
    sold_at: str


# Routes
@router.get("/items", response_model=List[ItemSchema])
def get_items(db: Session = Depends(get_db)):
    """Получение списка всех артефактов."""
    items = db.query(Item).all()
    return items


@router.get("/items/{item_id}/stats", response_model=ItemStatsSchema)
def get_item_stats(item_id: str, db: Session = Depends(get_db)):
    """Получение статистики артефакта."""
    stats = db.query(ItemStats).filter_by(
        item_id=item_id,
        region="RU"  # Можно сделать динамическим
    ).first()
    
    if not stats:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Статистика не найдена")
    
    return stats


@router.get("/items/{item_id}/lots", response_model=List[LotSnapshotSchema])
def get_item_lots(item_id: str, db: Session = Depends(get_db)):
    """Получение лотов артефакта."""
    lots = db.query(LotSnapshot).filter_by(
        item_id=item_id,
        region="RU"
    ).order_by(LotSnapshot.unit_price).limit(60).all()
    return lots


@router.get("/items/{item_id}/sales", response_model=List[SaleSchema])
def get_item_sales(item_id: str, db: Session = Depends(get_db)):
    """Получение продаж артефакта."""
    sales = db.query(Sale).filter_by(
        item_id=item_id,
        region="RU"
    ).order_by(Sale.sold_at.desc()).limit(50).all()
    return sales


@router.get("/catalog")
def get_catalog(db: Session = Depends(get_db)):
    """Получение каталога с статистикой."""
    items = db.query(Item).all()
    result = []
    
    for item in items:
        stats = db.query(ItemStats).filter_by(
            item_id=item.id,
            region="RU"
        ).first()
        
        if stats:
            result.append({
                "id": item.id,
                "name_ru": item.name_ru,
                "name_en": item.name_en,
                "category": item.category,
                "icon": item.icon,
                "market_price": stats.market_price,
                "liquidity": stats.liquidity,
                "change_24h": stats.change_24h,
                "active_lots": stats.active_lots
            })
    
    return {"items": result}
