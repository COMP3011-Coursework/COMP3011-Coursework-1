# Global Food Price Monitor

A full-stack web application for monitoring global food prices using WFP (World Food Programme) data. Built for COMP3011 Web Services and Web Data, University of Leeds.

## Features

- **Interactive choropleth map** — Countries coloured by food crisis score (covers ~99 WFP-monitored countries; developed nations appear gray as they are not tracked by WFP)
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

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.14 | managed via conda |
| Node.js | 22 | npm 10 |
| Docker | 24+ | with Compose V2 plugin (`docker compose`) |
| conda | any | used to create the Python environment |

### Python environment

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

### Frontend dependencies

```bash
npm install --prefix frontend
```

## Development

The recommended approach is to run only the database in Docker and the backend/frontend natively.

### 1. Start the database

```bash
cp .env.example .env          # fill in SECRET_KEY and passwords
docker compose up db -d
```

### 2. Start the backend

```bash
conda activate COMP3011-Coursework-1
./run-backend.sh
```

Runs `uvicorn app.main:app --reload`. On first boot the app automatically downloads WFP data from HDX and seeds the database — no manual step required.

- API: <http://localhost:8000/api/v1/>
- Docs: <http://localhost:8000/docs>

### 3. Start the frontend

```bash
./run-frontend.sh
```

Runs `npm run dev` inside `frontend/`. Reads `VITE_API_URL` from `.env` in the project root.

- App: <http://localhost:5173>

## Production

```bash
cp .env.example .env          # fill in SECRET_KEY, passwords, CORS_ORIGINS
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

The production compose override removes the source-code bind mount, runs uvicorn with 2 workers, and builds the frontend as a static nginx image.

| Service | URL |
| --- | --- |
| Frontend (nginx) | <http://localhost:80> |
| API | <http://localhost:8000/api/v1/> |
| API docs | <http://localhost:8000/docs> |

## Environment variables

Copy `.env.example` and fill in values:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Docker Compose DB config |

## API reference

Interactive docs at `/docs` (Swagger UI) and `/redoc`. Full endpoint reference: [docs/api-reference.md](docs/api-reference.md).

## Advanced features

Beyond basic CRUD, the application provides analytics endpoints and an MCP server for LLM integration. See [docs/advanced-features.md](docs/advanced-features.md) for full details.

**Analytics** — five endpoints covering price trends, commodity volatility, regional price comparison, market summaries, and composite crisis scores.

**MCP server** — mounted at `/mcp/sse`, exposing five tools (`get_global_crisis_overview`, `get_crisis_summary`, `get_price_trends`, `compare_regional_prices`, `get_volatile_commodities`) for use with Claude Desktop or any MCP-compatible client.

## Tests

Requires a running PostgreSQL instance (a separate test database is created automatically).

```bash
conda activate COMP3011-Coursework-1
cd backend
python -m pytest
python -m pytest --cov=app --cov-report=term-missing   # with coverage
```

Target: 100% coverage.
