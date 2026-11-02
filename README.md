# Prelestgram

Приватный мессенджер в стиле Telegram для своего сервера (≤10 человек).
С настоящим Telegram связан **только** через бота администратора — он выдаёт номера и присылает коды входа.
Никаких реальных SMS, оплат, Telegram Stars или TON: звёзды, подарки, NFT и премиум выдаёт только админ.

## Стек

| Часть | Технологии |
|---|---|
| Android | Kotlin, Jetpack Compose, Retrofit/OkHttp, WebSocket |
| API | FastAPI, SQLAlchemy 2 (async), Alembic |
| Данные | PostgreSQL 16, Redis 7, MinIO |
| Админ-бот | aiogram 3 |
| Сборка | GitHub Actions → APK (debug + release) |

## Как устроен вход

1. Человек пишет `/start` боту в настоящем Telegram.
2. Админ в боте выдаёт ему номер, например `+70000000001`.
3. Человек вводит номер в Prelestgram → сервер генерирует 6-значный код и бот присылает его в Telegram.
4. Код введён → аккаунт создан (или выполнен вход на новом устройстве).

## Быстрый старт сервера

```bash
cp .env.example .env      # заполни пароли, SECRET_KEY, BOT_TOKEN, ADMIN_TELEGRAM_IDS
docker compose up -d --build
curl http://localhost:8000/api/health
```

Миграции БД применяются автоматически при старте контейнера `backend`.

## Структура репозитория

```
prelestgram/
├── docker-compose.yml       # postgres, redis, minio, backend (+ bot с этапа 2)
├── .env.example             # вся конфигурация
├── backend/
│   ├── app/
│   │   ├── core/            # настройки, логирование, Redis
│   │   ├── db/              # движок и базовые классы ORM
│   │   ├── models/          # все таблицы
│   │   ├── api/             # REST и WebSocket
│   │   └── main.py
│   └── alembic/             # миграции
├── android/                 # с этапа 5
└── .github/workflows/       # backend.yml — проверка сервера; android.yml — APK (с этапа 5)
```

## GitHub Actions

- **Backend CI** — на каждый пуш в `backend/`: миграции на PostgreSQL 16 (вверх → проверка → откат → снова вверх), запуск API и `/api/health`, сборка Docker-образа.
- **Android CI** — появится на этапе 5: debug- и release-APK как артефакты сборки.
