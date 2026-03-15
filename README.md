# Global Food Price Monitor

A full-stack web application for monitoring global food prices using WFP (World Food Programme) data. Built for COMP3011 Web Services and Web Data, University of Leeds.

## Features

- **Interactive choropleth map** — Countries coloured by food crisis score
- **Price explorer** — Filter and paginate WFP price records by country, commodity, and date
- **Data entry** — Authenticated CRUD for price records
- **Crisis scoring** — Composite algorithm (volatility + trend + breadth) ranked across all countries
- **MCP server** — 5 LLM tools exposed over SSE for use with Claude Desktop

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend API | FastAPI + SQLAlchemy 2.x async |
| Database | PostgreSQL 17 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| MCP server | FastMCP (mounted inside FastAPI at `/mcp`) |
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS |
| Maps | Leaflet + react-leaflet |
| Charts | Chart.js + react-chartjs-2 |
| Deployment | Docker Compose |

---

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.14 | managed via conda |
| Node.js | 22 | npm 10 |
| Docker | 24+ | with Compose V2 plugin (`docker compose`) |
| conda | any | used to create the Python environment |

### Create the Python environment

**Recommended (conda):**

```bash
conda create -n COMP3011-Coursework-1 python=3.14
conda activate COMP3011-Coursework-1
pip install -r backend/requirements.txt
```

**Alternative (venv):**

```bash
python3.14 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
```

### Install frontend dependencies

```bash
npm install --prefix frontend
```

---

## Running in development

The easiest way to develop locally is to run only the database in Docker and the backend/frontend natively.

### 1. Start the database

```bash
cp .env.example .env          # fill in SECRET_KEY and passwords
docker compose up db -d
```

### 2. Backend

```bash
conda activate COMP3011-Coursework-1
./run-backend.sh
```

This runs `uvicorn app.main:app --reload`. On first boot the app automatically downloads WFP data from HDX and seeds the database — no manual seeding step required.

- API: <http://localhost:8000/api/v1/>
- Docs: <http://localhost:8000/docs>

### 3. Frontend

```bash
./run-frontend.sh
```

This runs `npm run dev` inside `frontend/`. The frontend reads `VITE_API_URL` from `.env` in the project root.

- App: <http://localhost:5173>

---

## Running in production (Docker)

```bash
cp .env.example .env          # fill in SECRET_KEY, passwords, CORS_ORIGINS
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

The production compose override:

- Removes the backend source-code bind mount (runs from the built image)
- Starts uvicorn with 2 workers
- Builds the frontend with `target: production` (nginx static build on port 80)

| Service | URL |
| --- | --- |
| Frontend (nginx) | <http://localhost:80> |
| API | <http://localhost:8000/api/v1/> |
| API docs | <http://localhost:8000/docs> |

---

## Environment variables

Copy `.env.example` and fill in values:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Docker Compose DB config |

---

## API reference

Interactive docs at `/docs` (Swagger UI) and `/redoc`.

### Authentication

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/v1/auth/register` | POST | Create account |
| `/api/v1/auth/login` | POST | Login, returns JWT |

A default admin account is created automatically on first boot:

| Field | Value |
| --- | --- |
| Username | `admin` |
| Password | `admin123` |

### Prices

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/api/v1/prices` | GET | — | List prices (filters: country, commodity_id, market_id, date_from, date_to, page, page_size) |
| `/api/v1/prices` | POST | ✓ | Create price record |
| `/api/v1/prices/{id}` | GET | — | Get single price |
| `/api/v1/prices/{id}` | PUT | ✓ | Update price |
| `/api/v1/prices/{id}` | DELETE | ✓ | Delete price |

### Analytics

| Endpoint | Description |
| --- | --- |
| `GET /api/v1/analytics/trends?country=&commodity_id=` | Monthly avg price time series |
| `GET /api/v1/analytics/volatility?country=` | Commodities ranked by price volatility (CoV) |
| `GET /api/v1/analytics/regional-comparison?commodity_id=` | Avg price per country |
| `GET /api/v1/analytics/crisis-scores` | All countries ranked by crisis score |
| `GET /api/v1/analytics/crisis-scores/{country}` | Single-country crisis breakdown |
| `GET /api/v1/analytics/markets/{market_id}/summary` | Market statistics |

### Reference data

| Endpoint | Description |
| --- | --- |
| `GET /api/v1/countries` | Countries with price data |
| `GET /api/v1/commodities` | All commodities |
| `GET /api/v1/markets?country=` | Markets (optionally filtered by country) |

### Crisis score algorithm

```text
volatility = avg(stddev/mean) per commodity over trailing 12 months
trend      = (latest 3-month avg) / (trailing 12-month avg) − 1
breadth    = fraction of commodities with latest price > trailing mean

Each component min-max normalised across all countries.
crisis_score = (0.40 × vol + 0.35 × trend + 0.25 × breadth) × 100
```

Severity: stable (0–25) · moderate (25–50) · high (50–75) · critical (75–100)

> **Map coverage note:** The choropleth map shows only the ~99 countries monitored by WFP. Developed nations (USA, UK, EU, Australia, etc.) are not tracked by WFP and will always appear gray — this reflects the source data.

---

## MCP server

The FastMCP server is mounted at `/mcp/sse`. Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "food-price-monitor": {
      "url": "http://localhost:8000/mcp/sse"
    }
  }
}
```

Available tools: `get_global_crisis_overview`, `get_crisis_summary`, `get_price_trends`, `compare_regional_prices`, `get_volatile_commodities`.

---

## Running tests

Tests require a running PostgreSQL instance (separate test DB is created automatically).

```bash
# activate test environment
conda activate COMP3011-Coursework-1
cd backend

# run all tests
python -m pytest

# with coverage report
python -m pytest --cov=app --cov-report=term-missing
```

Target: 100% coverage.
