# Market Insight PWA/Desktop

Централизованная архитектура для оптимизации запросов к Stalcraft API.

## Архитектура

```
Stalcraft API (45 req/min)
    ↓
Backend Collector (Render)
    ↓
PostgreSQL (кэш)
    ↓
WebSocket → 100+ клиентов
    ↓
PWA/Desktop приложения
```

## Преимущества

- **Один backend** = один набор лимитов API
- Все клиенты получают данные от backend через WebSocket
- Backend кэширует данные и делает умные запросы
- Если 100 пользователей - все равно только 45 запросов/мин к Stalcraft API
- PWA можно установить как приложение
- Офлайн режим с кэшированными данными
- Не нужен веб-хостинг для фронтенда

## Структура проекта

- `backend/` - FastAPI backend с коллектором и WebSocket
- `frontend/` - Next.js PWA приложение
- `shared/` - Общие типы и схемы

## Технологии

- **Backend**: FastAPI, PostgreSQL, WebSocket
- **Frontend**: Next.js, PWA, WebSocket client
- **Deployment**: Render (backend), GitHub Pages или Desktop (frontend)

## Деплой Backend (Render)

1. Создай репозиторий на GitHub
2. Загрузи код backend
3. Зайди на render.com → New Blueprint
4. Подключи GitHub репозиторий
5. Render автоматически найдет `render.yaml`
6. Настрой переменные окружения:
   - `MI_STALCRAFT_CLIENT_ID`
   - `MI_STALCRAFT_CLIENT_SECRET`
   - `MI_STALCRAFT_API_TOKEN`
7. Деплой

## Деплой Frontend (PWA)

### Вариант 1: GitHub Pages (бесплатно)

1. Билд: `cd frontend && npm run build`
2. Скопируй `out/` или `.next/` в отдельную ветку
3. Включи GitHub Pages в настройках репозитория
4. PWA доступна по `username.github.io/repo-name`

### Вариант 2: Desktop приложение (Electron/Tauri)

```bash
cd frontend
npm install -D electron electron-builder
npm run build
npm run package
```

### Вариант 3: Локальная установка PWA

1. Билд: `npm run build`
2. Запусти локальный сервер: `npm start`
3. Открой в Chrome → Установить как приложение
4. PWA работает офлайн с кэшем

## Настройка переменных окружения Frontend

Создай `.env.local` в `frontend/`:
```
NEXT_PUBLIC_API_URL=ws://your-backend-url.onrender.com
```

## Запуск локально

### Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```
