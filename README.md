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

## Quick start (Docker)

```bash
cp .env.example .env          # edit SECRET_KEY and passwords
docker-compose up --build
```

- Frontend: <http://localhost:5173>
- API docs: <http://localhost:8000/docs>
- API: <http://localhost:8000/api/v1/>

### Download GeoJSON (required for map)

The countries GeoJSON is not committed (14 MB). Download it once:

```bash
curl -sL https://raw.githubusercontent.com/datasets/geo-countries/main/data/countries.geojson \
  -o frontend/public/data/world.geojson
```

---

## Local development

### Backend

```bash
conda activate COMP3011-Coursework-1

cd backend
# Run database migrations
alembic upgrade head

# Seed with WFP data (CSV files from https://data.humdata.org/dataset/wfp-food-prices)
python scripts/seed.py /path/to/wfp-csv-files/

# Start API server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
# For local dev without Docker, create .env.local:
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

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
conda activate COMP3011-Coursework-1
cd backend

TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/food_monitor_test" \
  pytest --cov=app --cov-report=term-missing -v
```

Target: ≥80% coverage on routers and services.
