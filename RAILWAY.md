# Деплой на Railway

## Шаг 1 — Создай аккаунт и проект

1. Зайди на [railway.app](https://railway.app) → Sign in with GitHub
2. New Project → Deploy from GitHub repo → выбери этот репозиторий

---

## Шаг 2 — Добавь PostgreSQL и Redis

В проекте нажми **+ New** и добавь:
- **PostgreSQL** — Railway автоматически задаст `DATABASE_URL`
- **Redis** — Railway автоматически задаст `REDIS_URL`

---

## Шаг 3 — Создай 4 сервиса из репозитория

Для каждого нажми **+ New → GitHub Repo → выбери репо**, затем настрой:

### Backend (API)
- **Root Directory:** `backend`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Worker (Celery)
- **Root Directory:** `backend`
- **Start Command:** `celery -A app.workers.celery_app worker --loglevel=info`

### Beat (Scheduler)
- **Root Directory:** `backend`
- **Start Command:** `celery -A app.workers.celery_app beat --loglevel=info`

### Frontend
- **Root Directory:** `frontend`
- **Build Args:** `VITE_API_URL=https://ВАШ-BACKEND-ДОМЕН.railway.app`

---

## Шаг 4 — Переменные окружения

Для сервисов **backend**, **worker**, **beat** добавь в Variables:

```
APP_ENV=production
SECRET_KEY=<openssl rand -hex 32>
FERNET_KEY=<python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
OPENAI_API_KEY=sk-...
INSTAGRAM_APP_ID=...
INSTAGRAM_APP_SECRET=...
INSTAGRAM_REDIRECT_URI=https://ВАШ-BACKEND.railway.app/api/v1/accounts/instagram/callback

# DATABASE_URL и REDIS_URL Railway подставит сам через shared variables
# Но нужно добавить вручную:
SYNC_DATABASE_URL=${{Postgres.DATABASE_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
```

> Используй Railway Variables Reference (`${{Postgres.DATABASE_URL}}`) чтобы автоматически получать URL от плагинов.

---

## Шаг 5 — Запусти миграции

После первого деплоя бэкенда открой **Railway Shell** для backend-сервиса и выполни:

```bash
alembic upgrade head
```

---

## Готово!

- Frontend: `https://ВАШ-ФРОНТЕНД.railway.app`
- API docs: `https://ВАШ-БЕКЕНД.railway.app/docs`

---

## Примерная стоимость на Railway

| Сервис | ~$/месяц |
|---|---|
| Backend | $5 |
| Worker | $3 |
| Beat | $1 |
| Frontend | $2 |
| PostgreSQL | $5 |
| Redis | $3 |
| **Итого** | **~$19** |

Hobby план даёт $5 кредитов бесплатно каждый месяц.
