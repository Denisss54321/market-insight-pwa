"""Подключение к базе данных."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Iterator

from app.config import settings

# Настройка для PostgreSQL на Render
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def get_db() -> Iterator[Session]:
    """Получение сессии базы данных."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Инициализация базы данных."""
    from app.models import Base
    from sqlalchemy import text
    
    Base.metadata.create_all(bind=engine)
    
    # Добавляем миграции для PostgreSQL
    with engine.connect() as conn:
        try:
            # Проверяем наличие колонки first_seen_at в lot_snapshots
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'lot_snapshots' AND column_name = 'first_seen_at'
            """))
            if result.fetchone() is None:
                conn.execute(text("ALTER TABLE lot_snapshots ADD COLUMN first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
                
            # Проверяем nullable для market_price в item_stats
            result = conn.execute(text("""
                SELECT is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'item_stats' AND column_name = 'market_price'
            """))
            row = result.fetchone()
            if row and row[0] == 'NO':
                conn.execute(text("ALTER TABLE item_stats ALTER COLUMN market_price DROP NOT NULL"))
                conn.execute(text("ALTER TABLE item_stats ALTER COLUMN median DROP NOT NULL"))
                conn.execute(text("ALTER TABLE item_stats ALTER COLUMN mean DROP NOT NULL"))
                conn.execute(text("ALTER TABLE item_stats ALTER COLUMN mode DROP NOT NULL"))
                conn.commit()
                
        except Exception as e:
            print(f"Migration error: {e}")
            conn.rollback()
