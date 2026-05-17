# AI Social Content Engine — Project Specification for Claude Code

## Project Overview

Build an AI-powered visual content generation and publishing system for social media.
The system analyzes engagement data, generates personalized content (text + images),
publishes it via official APIs, monitors feedback, and self-adjusts its content strategy.

---

## Tech Stack (Non-Negotiable)

```
Backend:     Python 3.11+, FastAPI, Celery, Redis
ML/AI:       PyTorch, scikit-learn, HuggingFace Transformers
LLM:         OpenAI API (gpt-4o-mini) — abstracted behind interface for future swap to Ollama
Image gen:   OpenAI DALL-E 3 API — abstracted behind interface for future swap to Stable Diffusion
Database:    PostgreSQL 16 + pgvector extension + Redis 7
Frontend:    React 18 + TypeScript + Tailwind CSS + Recharts
Queue:       Celery + Redis (broker + result backend)
Deploy:      Docker Compose (dev), ready for single-VPS production
Social APIs: Instagram Graph API v21+, YouTube Data API v3, Reddit API (PRAW)
Storage:     Local filesystem (dev), S3-compatible interface (prod-ready)
```

---

## Repository Structure

Create exactly this structure. Do not deviate.

```
ai-social-engine/
├── CLAUDE.md                          # This file
├── docker-compose.yml                 # Full dev environment
├── docker-compose.prod.yml            # Production overrides
├── .env.example                       # All required env vars with comments
├── .gitignore
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/                  # DB migrations
│   │
│   ├── app/
│   │   ├── main.py                    # FastAPI app factory
│   │   ├── config.py                  # Settings via pydantic-settings
│   │   ├── database.py                # SQLAlchemy async engine + session
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── social_account.py
│   │   │   ├── post.py
│   │   │   ├── analytics.py
│   │   │   └── content_strategy.py
│   │   │
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── post.py
│   │   │   ├── analytics.py
│   │   │   └── generation.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # Shared dependencies (auth, db session)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py          # Aggregates all routers
│   │   │       ├── auth.py            # JWT auth endpoints
│   │   │       ├── accounts.py        # Social account connect/disconnect
│   │   │       ├── posts.py           # Post CRUD + scheduling
│   │   │       ├── generation.py      # AI content generation endpoints
│   │   │       ├── analytics.py       # Metrics + reports endpoints
│   │   │       └── strategy.py        # Content strategy management
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_llm.py        # Abstract LLM interface
│   │   │   │   ├── openai_llm.py      # OpenAI implementation
│   │   │   │   ├── ollama_llm.py      # Ollama implementation (stub, ready to fill)
│   │   │   │   ├── base_image.py      # Abstract image gen interface
│   │   │   │   ├── dalle_image.py     # DALL-E 3 implementation
│   │   │   │   ├── sd_image.py        # Stable Diffusion stub
│   │   │   │   └── content_generator.py  # Orchestrates text + image generation
│   │   │   │
│   │   │   ├── social/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_platform.py   # Abstract platform interface
│   │   │   │   ├── instagram.py       # Instagram Graph API v21 client
│   │   │   │   ├── youtube.py         # YouTube Data API v3 client
│   │   │   │   └── reddit.py          # Reddit PRAW client
│   │   │   │
│   │   │   ├── analytics/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── collector.py       # Pulls metrics from platforms
│   │   │   │   ├── aggregator.py      # Aggregates + stores metrics
│   │   │   │   └── reporter.py        # Generates reports
│   │   │   │
│   │   │   └── ml/
│   │   │       ├── __init__.py
│   │   │       ├── feature_engineering.py   # Feature extraction from posts/metrics
│   │   │       ├── engagement_predictor.py  # LightGBM model: predicts engagement
│   │   │       ├── optimal_time.py          # Best time-to-post recommender
│   │   │       ├── sentiment_analyzer.py    # HuggingFace BERT for comments
│   │   │       ├── strategy_optimizer.py    # Feedback loop: adjusts content plan
│   │   │       └── model_store.py           # Save/load trained models
│   │   │
│   │   └── workers/
│   │       ├── __init__.py
│   │       ├── celery_app.py          # Celery application instance
│   │       ├── publish_task.py        # Scheduled post publication
│   │       ├── analytics_task.py      # Periodic metrics collection
│   │       ├── strategy_task.py       # Weekly strategy recalculation
│   │       └── generation_task.py     # Async content generation
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_api/
│       └── test_services/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       │
│       ├── api/
│       │   ├── client.ts              # Axios instance with interceptors
│       │   ├── auth.ts
│       │   ├── posts.ts
│       │   ├── analytics.ts
│       │   └── generation.ts
│       │
│       ├── store/
│       │   ├── authStore.ts           # Zustand auth state
│       │   ├── postStore.ts
│       │   └── analyticsStore.ts
│       │
│       ├── pages/
│       │   ├── Dashboard.tsx          # Main metrics overview
│       │   ├── ContentCalendar.tsx    # Visual post schedule
│       │   ├── Generator.tsx          # AI content creation UI
│       │   ├── Analytics.tsx          # Engagement charts
│       │   ├── Accounts.tsx           # Social account management
│       │   └── Login.tsx
│       │
│       └── components/
│           ├── layout/
│           │   ├── Sidebar.tsx
│           │   └── TopBar.tsx
│           ├── charts/
│           │   ├── EngagementChart.tsx
│           │   ├── PostPerformanceChart.tsx
│           │   └── BestTimeHeatmap.tsx
│           ├── posts/
│           │   ├── PostCard.tsx
│           │   ├── PostEditor.tsx
│           │   └── SchedulePicker.tsx
│           └── generation/
│               ├── GenerationForm.tsx
│               └── ContentPreview.tsx
│
└── ml_notebooks/
    ├── 01_feature_exploration.ipynb
    ├── 02_engagement_model_training.ipynb
    └── 03_sentiment_analysis_setup.ipynb
```

---

## Database Schema

Implement these tables via SQLAlchemy models + Alembic migrations.

### Table: `users`
```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
email         VARCHAR(255) UNIQUE NOT NULL
password_hash VARCHAR(255) NOT NULL
created_at    TIMESTAMPTZ DEFAULT now()
updated_at    TIMESTAMPTZ DEFAULT now()
is_active     BOOLEAN DEFAULT true
```

### Table: `social_accounts`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID REFERENCES users(id) ON DELETE CASCADE
platform        VARCHAR(50) NOT NULL  -- 'instagram' | 'youtube' | 'reddit'
platform_user_id VARCHAR(255) NOT NULL
username        VARCHAR(255)
access_token    TEXT NOT NULL          -- encrypted at rest
refresh_token   TEXT
token_expires_at TIMESTAMPTZ
account_type    VARCHAR(50)            -- 'business' | 'creator' | 'personal'
is_active       BOOLEAN DEFAULT true
connected_at    TIMESTAMPTZ DEFAULT now()
metadata        JSONB DEFAULT '{}'     -- platform-specific extra data
UNIQUE(user_id, platform, platform_user_id)
```

### Table: `posts`
```sql
id                UUID PRIMARY KEY DEFAULT gen_random_uuid()
social_account_id UUID REFERENCES social_accounts(id) ON DELETE CASCADE
user_id           UUID REFERENCES users(id)
status            VARCHAR(50) DEFAULT 'draft'  -- draft|scheduled|published|failed
platform_post_id  VARCHAR(255)                 -- ID returned by platform after publish
content_text      TEXT
image_url         TEXT
image_local_path  TEXT
scheduled_at      TIMESTAMPTZ
published_at      TIMESTAMPTZ
generation_params JSONB DEFAULT '{}'           -- topic, tone, style, etc.
content_vector    VECTOR(1536)                 -- pgvector embedding for similarity
created_at        TIMESTAMPTZ DEFAULT now()
error_message     TEXT
```

### Table: `post_metrics`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
post_id         UUID REFERENCES posts(id) ON DELETE CASCADE
collected_at    TIMESTAMPTZ DEFAULT now()
likes           INTEGER DEFAULT 0
comments        INTEGER DEFAULT 0
shares          INTEGER DEFAULT 0
saves           INTEGER DEFAULT 0
reach           INTEGER DEFAULT 0
impressions     INTEGER DEFAULT 0
watch_through_rate FLOAT                        -- for video content
engagement_rate FLOAT GENERATED ALWAYS AS      -- computed column
  (CASE WHEN reach > 0
   THEN (likes + comments + shares + saves)::float / reach
   ELSE 0 END) STORED
raw_data        JSONB DEFAULT '{}'
```

### Table: `content_strategies`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID REFERENCES users(id)
social_account_id UUID REFERENCES social_accounts(id)
strategy_data   JSONB NOT NULL    -- topics, frequencies, styles, best_times
model_version   VARCHAR(50)
created_at      TIMESTAMPTZ DEFAULT now()
is_active       BOOLEAN DEFAULT true
```

### Enable pgvector:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## Environment Variables

`.env.example` must contain ALL of these with explanatory comments:

```bash
# === Application ===
APP_ENV=development                    # development | production
SECRET_KEY=changeme-use-openssl-rand   # JWT signing key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# === Database ===
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/social_engine
SYNC_DATABASE_URL=postgresql://postgres:postgres@db:5432/social_engine  # for Alembic

# === Redis ===
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# === OpenAI ===
OPENAI_API_KEY=sk-...
OPENAI_TEXT_MODEL=gpt-4o-mini
OPENAI_IMAGE_MODEL=dall-e-3
OPENAI_IMAGE_SIZE=1024x1024            # 1024x1024 | 1792x1024 | 1024x1792

# === Instagram Graph API ===
INSTAGRAM_APP_ID=
INSTAGRAM_APP_SECRET=
INSTAGRAM_REDIRECT_URI=http://localhost:8000/api/v1/accounts/instagram/callback

# === YouTube Data API ===
YOUTUBE_API_KEY=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=

# === Reddit API ===
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=social-engine:v1.0

# === Storage ===
MEDIA_STORAGE_PATH=./media             # local path for dev
# S3_BUCKET=                           # uncomment for prod
# S3_REGION=
# S3_ACCESS_KEY=
# S3_SECRET_KEY=
# S3_ENDPOINT_URL=                     # for Cloudflare R2 / MinIO

# === ML ===
ML_MODELS_PATH=./ml_models             # where trained models are saved
ENGAGEMENT_MODEL_MIN_SAMPLES=50        # min posts before ML kicks in
```

---

## Core Implementation Requirements

### 1. AI Content Generator (`services/ai/content_generator.py`)

Must implement this interface:

```python
class ContentGenerator:
    async def generate_post(
        self,
        topic: str,
        platform: str,           # 'instagram' | 'youtube' | 'reddit'
        tone: str,               # 'professional' | 'casual' | 'humorous' | 'inspirational'
        style_hints: list[str],  # e.g. ['minimalist', 'bright colors', 'people']
        account_history: list[dict] | None = None,  # past top posts for context
        strategy: dict | None = None,
    ) -> GeneratedContent:
        # Returns: text, image_prompt, generated_image_url, hashtags, estimated_engagement
```

- Text generation: use system prompt that includes platform best practices (Instagram ≤2200 chars, optimal hashtag count per platform)
- Image generation: always generate image_prompt separately, then pass to image generator
- If `account_history` provided: extract style/tone patterns and include in prompt
- Implement retry logic (3 attempts) with exponential backoff for API calls
- Log token usage per generation to database

### 2. Instagram Client (`services/social/instagram.py`)

Required methods:
```python
class InstagramClient:
    async def publish_photo(self, account: SocialAccount, image_url: str, caption: str) -> str
    async def publish_reel(self, account: SocialAccount, video_url: str, caption: str) -> str
    async def get_post_insights(self, account: SocialAccount, post_id: str) -> dict
    async def get_account_insights(self, account: SocialAccount, period: str) -> dict
    async def refresh_token(self, account: SocialAccount) -> SocialAccount
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict
```

- Instagram Graph API base URL: `https://graph.instagram.com/v21.0`
- Two-step publish for photos: (1) create container, (2) publish container
- Rate limit handling: respect 200 calls/hour, implement backoff
- Token refresh: long-lived tokens expire in 60 days — implement auto-refresh with 7-day buffer
- Only Business/Creator accounts supported — validate on connect

### 3. Celery Tasks (`workers/`)

```python
# publish_task.py
@celery_app.task(bind=True, max_retries=3)
def publish_scheduled_post(self, post_id: str) -> dict:
    # Load post, select platform client, publish, update status, trigger analytics collection

# analytics_task.py  
@celery_app.task
def collect_post_metrics(post_id: str) -> dict:
    # Called: 1h, 6h, 24h, 7d after publish — collect metrics at each interval

@celery_app.task
def collect_all_pending_metrics() -> None:
    # Beat schedule: every hour — find published posts needing metric update

# strategy_task.py
@celery_app.task
def recalculate_strategy(user_id: str, social_account_id: str) -> dict:
    # Beat schedule: every Monday 02:00 — rerun ML models, update strategy
```

Celery Beat schedule:
- Every 5 min: check and publish due scheduled posts
- Every hour: collect pending metrics
- Every Monday 02:00 UTC: recalculate all strategies

### 4. Engagement Predictor (`services/ml/engagement_predictor.py`)

```python
class EngagementPredictor:
    def train(self, posts_df: pd.DataFrame) -> dict:  # returns metrics
    def predict(self, features: dict) -> float:       # returns predicted engagement_rate
    def get_feature_importance(self) -> dict
```

Features to extract (in `feature_engineering.py`):
- `hour_of_day` (0-23)
- `day_of_week` (0-6)
- `text_length`
- `hashtag_count`
- `has_image` (bool)
- `image_brightness` (0-1, via PIL)
- `image_colorfulness` (float)
- `text_sentiment` (float, -1 to 1)
- `topic_category` (encoded)
- `account_avg_engagement_7d`
- `account_post_frequency_7d`

Model: start with LightGBM (`lightgbm` package). Only train when `ENGAGEMENT_MODEL_MIN_SAMPLES` posts available. Fall back to heuristic-based scoring before that.

### 5. Strategy Optimizer (`services/ml/strategy_optimizer.py`)

```python
class StrategyOptimizer:
    def generate_weekly_plan(
        self,
        account_id: str,
        posts_history: list,
        metrics_history: list,
        current_strategy: dict | None,
    ) -> ContentStrategy:
```

Output `ContentStrategy` must include:
```json
{
  "best_post_times": [{"day": "monday", "hours": [9, 18]}, ...],
  "recommended_topics": ["topic1", "topic2"],
  "recommended_tone": "casual",
  "recommended_frequency": 7,
  "content_mix": {"photo": 0.5, "carousel": 0.3, "video": 0.2},
  "underperforming_patterns": ["long captions", "dark images"],
  "ab_test_suggestion": {"variable": "tone", "variants": ["casual", "inspirational"]}
}
```

Feedback loop trigger: if post gets engagement_rate < 50% of predicted → flag for strategy review.

---

## API Endpoints

All endpoints under `/api/v1/`. Implement with FastAPI async handlers.

### Auth
```
POST   /auth/register
POST   /auth/login          → returns JWT access + refresh tokens
POST   /auth/refresh
POST   /auth/logout
```

### Social Accounts
```
GET    /accounts                        → list connected accounts
POST   /accounts/instagram/connect      → initiate OAuth flow
GET    /accounts/instagram/callback     → OAuth callback handler
DELETE /accounts/{account_id}
GET    /accounts/{account_id}/status    → token validity, last sync
```

### Content Generation
```
POST   /generation/generate             → body: {topic, platform, tone, style_hints, account_id}
                                        → returns: {text, image_url, hashtags, estimated_engagement}
POST   /generation/regenerate/{post_id} → regenerate for existing draft
POST   /generation/batch                → generate content plan (7 posts) for a week
```

### Posts
```
GET    /posts                           → list posts (filter: status, account_id, date range)
POST   /posts                           → create post (draft or scheduled)
GET    /posts/{post_id}
PUT    /posts/{post_id}
DELETE /posts/{post_id}
POST   /posts/{post_id}/publish-now    → immediate publish
POST   /posts/{post_id}/schedule       → body: {scheduled_at}
GET    /posts/{post_id}/metrics        → all collected metrics snapshots
```

### Analytics
```
GET    /analytics/overview             → summary stats for dashboard
GET    /analytics/engagement-trend     → time series, params: account_id, days=30
GET    /analytics/best-times           → heatmap data: day × hour → avg engagement
GET    /analytics/top-posts            → top N posts by engagement_rate
GET    /analytics/content-performance  → breakdown by content type / topic / tone
POST   /analytics/export               → generate CSV report
```

### Strategy
```
GET    /strategy/{account_id}          → current strategy
POST   /strategy/{account_id}/recalculate → trigger manual recalculation
GET    /strategy/{account_id}/history  → past strategies
```

---

## Frontend Pages

### Dashboard (`/`)
- Stat cards: total posts this week, avg engagement rate, best performing post, predicted engagement next post
- Line chart: engagement rate over last 30 days (Recharts LineChart)
- Bar chart: posts published per day last 14 days
- Quick action button: "Generate Post"

### Content Calendar (`/calendar`)
- 7-day grid view (week) and 30-day grid (month)
- Each post shows: thumbnail, platform icon, status badge (draft/scheduled/published)
- Click post → open PostEditor sidebar
- "+" on any day/time slot → open GenerationForm

### Generator (`/generate`)
- Form fields: Topic (text), Platform (select), Tone (select), Style hints (tag input)
- "Generate" button → loading state → preview card shows generated text + image
- Preview card has: Edit text area, "Regenerate image", "Regenerate text", "Schedule" button
- Schedule picker: calendar + time selector

### Analytics (`/analytics`)
- Engagement trend line chart (date range picker: 7d/30d/90d)
- Best times heatmap (day × hour grid, color = avg engagement)
- Top posts table: thumbnail, text snippet, platform, likes, comments, saves, engagement_rate
- Content mix donut chart: photo vs video vs carousel

### Accounts (`/accounts`)
- Connected accounts list with: avatar, username, platform, account_type, token status
- "Connect Instagram" button → opens OAuth flow
- Token expiry warning badge (< 7 days)

---

## Docker Compose

`docker-compose.yml` must define these services:

```yaml
services:
  db:          # postgres:16-alpine, port 5432, with pgvector
  redis:       # redis:7-alpine, port 6379
  backend:     # built from ./backend, port 8000, hot reload
  worker:      # same image as backend, runs celery worker
  beat:        # same image as backend, runs celery beat
  frontend:    # built from ./frontend, port 3000, hot reload
```

All services on same Docker network `social-engine-net`.
Backend waits for DB and Redis via healthchecks.
Use named volume for PostgreSQL data persistence.

---

## Implementation Order (follow strictly)

1. `docker-compose.yml` + `Dockerfile` files for both services
2. `.env.example` with all variables
3. Database models + initial Alembic migration
4. FastAPI app skeleton + auth endpoints (register/login/JWT)
5. Social account model + Instagram OAuth flow
6. OpenAI LLM service + DALL-E image service + ContentGenerator
7. Post model + generation endpoint (POST /generation/generate)
8. Celery app + publish task + schedule endpoint
9. Analytics collector + post_metrics model + metrics endpoints
10. ML feature engineering + LightGBM engagement predictor
11. Strategy optimizer + strategy endpoints
12. All remaining API endpoints (CRUD completeness)
13. React frontend: routing + auth pages
14. Dashboard page with charts
15. Generator page
16. Content Calendar page
17. Analytics page
18. Accounts page
19. Integration tests (pytest + httpx)
20. README.md with setup instructions

---

## Code Quality Requirements

- All Python async (use `async def` + `asyncio` throughout — no blocking calls in async context)
- All database queries via SQLAlchemy async ORM (not raw SQL except for complex analytics aggregations)
- Pydantic v2 for all request/response validation
- Type hints on all functions (Python) and TypeScript strict mode on frontend
- No hardcoded secrets anywhere — all from `config.py` which reads `.env`
- Abstract interfaces for LLM and image generation (strategy pattern) — switching providers must require only changing config, not business logic
- Error handling: all API errors return `{"error": {"code": "...", "message": "..."}}` format
- Logging: structured JSON logs with `structlog`
- Each Celery task must be idempotent (safe to retry)

---

## Security Requirements

- Passwords: bcrypt hashing (passlib)
- JWT: RS256 or HS256 with proper expiry
- Social account tokens: encrypt at rest using Fernet (cryptography package) before storing in DB
- CORS: configured for frontend origin only
- Rate limiting on generation endpoints: 20 requests/hour per user (use slowapi)
- Input validation: all user inputs validated via Pydantic, no raw string interpolation in prompts

---

## README.md Requirements

Must include:
1. Architecture diagram (ASCII)
2. Prerequisites (Docker, Python 3.11+, Node 20+)
3. Quick start (5 commands to running system)
4. How to connect Instagram account (step-by-step with screenshots placeholders)
5. API documentation link (points to `/docs` — FastAPI auto-docs)
6. Environment variables reference table
7. How to run tests
8. How to add a new social platform (extension guide)

---

## Out of Scope (do NOT implement)

- Payment/billing system
- Multi-tenancy with organization accounts
- Mobile app
- Stable Diffusion local inference (stub only, marked TODO)
- TikTok API (stub interface only)
- Email notifications
- Webhooks

---

## Notes for Claude Code

- Start by reading this entire file before writing any code.
- If a requirement seems ambiguous, choose the more explicit/typed solution.
- When in doubt about file placement, follow the directory structure exactly.
- The ML components (engagement_predictor, strategy_optimizer) should work in degraded mode (rule-based fallback) when insufficient training data exists — never crash or block the publishing flow.
- Instagram OAuth requires HTTPS in production. For local dev, use the sandbox mode with test users.
- All dates/times stored in UTC in the database. Frontend handles timezone conversion.
