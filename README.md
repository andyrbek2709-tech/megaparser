# AI Social Content Engine

An AI-powered visual content generation and publishing system for social media. Analyzes engagement data, generates personalized content (text + images), publishes via official APIs, monitors feedback, and self-adjusts its content strategy.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Frontend                         │
│         React 18 + TypeScript + Tailwind + Recharts     │
│  Dashboard | Calendar | Generator | Analytics | Accounts│
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────┐
│                     FastAPI Backend                      │
│  /api/v1: auth | accounts | posts | generation |         │
│           analytics | strategy                          │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  AI Services │  │Social Services│  │  ML Services  │  │
│  │  OpenAI LLM  │  │  Instagram   │  │  LightGBM     │  │
│  │  DALL-E 3    │  │  YouTube     │  │  Engagement   │  │
│  │  (pluggable) │  │  Reddit      │  │  Predictor    │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└───────────┬────────────────────────────────────────┬────┘
            │                                        │
┌───────────▼───────────┐              ┌─────────────▼────┐
│    Celery Workers      │              │   PostgreSQL 16   │
│  publish_task          │              │   + pgvector      │
│  analytics_task        │              │   + Redis 7       │
│  strategy_task         │              └──────────────────┘
└───────────────────────┘
```

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local dev without Docker)
- Node 20+ (for local frontend dev)

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your API keys

# 2. Start all services
docker-compose up -d

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Access the app
open http://localhost:3000

# 5. API documentation
open http://localhost:8000/docs
```

## Connect Instagram Account

1. Register at https://developers.facebook.com and create an app
2. Add Instagram Graph API product to your app
3. Set `INSTAGRAM_APP_ID` and `INSTAGRAM_APP_SECRET` in `.env`
4. Set redirect URI to `http://localhost:8000/api/v1/accounts/instagram/callback`
5. In the app UI, go to **Accounts** → **Connect Instagram**
6. Authorize through the OAuth flow
7. Only Business or Creator accounts are supported

## Environment Variables Reference

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) |
| `DATABASE_URL` | PostgreSQL async URL |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini and DALL-E 3 |
| `INSTAGRAM_APP_ID` | Meta Developer App ID |
| `FERNET_KEY` | Encryption key for stored tokens |
| `ENGAGEMENT_MODEL_MIN_SAMPLES` | Minimum posts before ML model trains (default: 50) |

See `.env.example` for the full list.

## Running Tests

```bash
# Backend tests
docker-compose exec backend pytest tests/ -v

# Or locally
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## Adding a New Social Platform

1. Create `backend/app/services/social/yourplatform.py` implementing `BasePlatform`
2. Add OAuth endpoints in `backend/app/api/v1/accounts.py`
3. Handle the platform in `backend/app/workers/publish_task.py`
4. Add platform to `PLATFORM_CONSTRAINTS` in `content_generator.py`
5. Update analytics collector in `services/analytics/collector.py`
