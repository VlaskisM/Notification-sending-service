# notification-service

Небольшой сервис для отправки уведомлений. HTTP API принимает запросы, складывает их в Postgres, кидает задачу в Celery, воркер забирает её и «отправляет» (сейчас просто помечает статус — заглушка под реальную интеграцию с провайдером).

Стек: Flask, SQLAlchemy 2 + Alembic, Celery + Redis, Postgres 17, Pydantic.

## Запуск

Понадобится только Docker.

```bash
cp .env.example .env
docker compose up --build
```

После того как контейнеры поднялись, нужно накатить миграции:

```bash
docker compose run --rm app alembic upgrade head
```

Дальше API доступен на `http://localhost:5001`.

Порт 5001 — потому что на macOS на 5000 висит AirPlay Receiver. Если у вас его нет, можно поменять проброс в `docker-compose.yml` обратно на `5000:5000`.

### Переменные окружения

В `.env.example` лежит шаблон. Главное:

- `POSTGRES_*` — креды и имя БД.
- `REDIS_HOST=redis` — внутри docker‑сети Redis доступен по имени сервиса. Если запускаете приложение прямо с хоста (без docker) — ставте `localhost`.
- `CELERY_BROKER_DB=0` — номер базы внутри Redis.
- `PAGINATION_*` — настройки пагинации для GET `/notifications`.

## API

Все эндпоинты под префиксом `/api/v1/notifications`.

### Создать уведомление

```bash
curl -X POST http://localhost:5001/api/v1/notifications/ \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "sms",
    "recipient": "+79991234567",
    "message": "test"
  }'
```

Поле `subject` опциональное, но для `email` обычно нужно. `type` должен быть один из `email`, `sms`, `telegram`.

Ответ:
```json
{ "id": "efe6dc15-5bbd-4636-adab-746b7d1b7598", "status": "queued", "error": null }
```

В этот момент запись уже в БД со статусом `queued`, задача — в очереди.

### Получить уведомление по id

```bash
curl http://localhost:5001/api/v1/notifications/efe6dc15-5bbd-4636-adab-746b7d1b7598
```

После того как воркер обработает задачу, статус станет `sent` или `failed`. В случае `failed` в поле `error` будет сообщение.

### Список уведомлений

```bash
curl 'http://localhost:5001/api/v1/notifications/?status=sent&limit=20&offset=0'
```

Все параметры опциональные. Если `status` не задан — возвращаются все. `limit` ограничен сверху значением `PAGINATION_MAX_LIMIT`.

## Архитектура

```
        HTTP
          │
          ▼
     ┌─────────┐    save     ┌──────────┐
     │  Flask  │ ──────────▶ │ Postgres │
     └─────────┘             └──────────┘
          │                        ▲
          │ publish                │ update status
          ▼                        │
       ┌──────┐  pop task     ┌────────┐
       │ Redis│ ────────────▶ │ Celery │
       └──────┘               │ worker │
                              └────────┘
```

Поток создания уведомления:

1. Flask принимает POST, валидирует тело через Pydantic + ручные правила (`app/validators/notification_validator.py`).
2. Сервисный слой (`app/services/service_notification.py`) сохраняет запись в Postgres через UoW + репозиторий.
3. Брокер (`app/message_broker/notification_broker.py`) кидает задачу `send_notification` в Celery — она уходит в Redis.
4. Воркер забирает задачу из Redis, выполняет (`app/tasks.py`), обновляет статус записи в Postgres синхронным движком SQLAlchemy.

Запросы на чтение (GET) идут только в Postgres, ни Celery, ни Redis не задействованы.

### Слои

- `routes/` — Flask blueprints, разбор HTTP и сериализация ответа. Бизнес‑логики тут нет.
- `services/` — оркестрация: валидация → запись → постановка в очередь.
- `repositories/` — работа с Postgres через SQLAlchemy. Снаружи отдают доменные модели (Pydantic), а не ORM‑объекты.
- `uow.py` — Unit of Work, на каждый запрос своя сессия и транзакция.
- `message_broker/` — абстракция над Celery, чтобы сервисный слой не зависел от конкретного брокера.
- `tasks.py` — Celery‑таски. Используют **синхронный** движок SQLAlchemy, потому что Celery работает в синхронных воркерах.
- `validators/` — доменные правила: разрешённые типы, формат получателя и т.д.
- `models.py` — ORM‑модели.
- `schemas.py` — Pydantic‑схемы входа/выхода.