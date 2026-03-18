# Global Food Price Monitor

A full-stack web application for monitoring global food prices using WFP (World Food Programme) data. Built for COMP3011 Web Services and Web Data, University of Leeds.

## Live demo

| Service | URL |
| --- | --- |
| Frontend | [comp3011-coursework-1-frontend.onrender.com](https://comp3011-coursework-1-frontend.onrender.com/) |
| Backend — API docs (Swagger) | [comp3011-coursework-1-backend.onrender.com/docs](https://comp3011-coursework-1-backend.onrender.com/docs) |
| Backend — API docs (ReDoc) | [comp3011-coursework-1-backend.onrender.com/redoc](https://comp3011-coursework-1-backend.onrender.com/redoc) |

> Hosted on Render's free plan — initial load may be slow due to cold starts and resource limits. Runs well locally.

Default admin credentials: username `admin`, password `admin123`.

## Features

- **Interactive choropleth map** — Countries coloured by food crisis score (covers ~99 WFP-monitored countries; developed nations appear gray as they are not tracked by WFP)
- **Price explorer** — Filter and paginate WFP price records by country, commodity, and date
- **Data entry** — Authenticated CRUD for price records
- **Crisis scoring** — Composite algorithm (volatility + trend + breadth) ranked across all countries
- **MCP server** — 5 LLM tools exposed over HTTP for use with Claude Code or Claude Desktop

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

## API reference

Interactive docs (`/docs` Swagger UI, `/redoc`, `/openapi.json`) are served directly from the backend. Endpoint index: [docs/api-index.md](docs/api-index.md). Full reference (PDF): [docs/api-reference.pdf](docs/api-reference.pdf).

## Advanced features

Beyond basic CRUD, the application provides analytics endpoints and an MCP server for LLM integration. See [docs/advanced-features.md](docs/advanced-features.md) for full details.

### Analytics

Five endpoints covering price trends, commodity volatility, regional price comparison, market summaries, and composite crisis scores.

### MCP server

Mounted at `/mcp/` (streamable HTTP transport), exposing five tools for use with Claude Code, Claude Desktop, or any MCP-compatible client.

#### Claude Code

Register the server once:

```bash
claude mcp add --transport http food-price http://localhost:8000/mcp/
```

Then inside a Claude Code session run `/mcp` to confirm the connection and 5 tools are listed. You can then ask Claude to call them directly, e.g.:

> "Use get_global_crisis_overview to show the top countries by food crisis score"

To use the live deployment instead:

```bash
claude mcp add --transport http food-price https://comp3011-coursework-1-backend.onrender.com/mcp/
```

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "food-price": {
      "type": "http",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

#### Available tools

| Tool | Description |
| --- | --- |
| `get_global_crisis_overview` | Top N countries ranked by composite crisis score |
| `get_crisis_summary` | Detailed crisis breakdown for a specific country |
| `get_price_trends` | Price trend over time for a commodity in a country |
| `compare_regional_prices` | Compare commodity prices across countries |
| `get_volatile_commodities` | Most price-volatile commodities globally or per country |

## Development

The recommended approach is to run only the database in Docker and the backend/frontend natively.

### Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Python | 3.14 | managed via conda |
| Node.js | 22 | npm 10 |
| Docker | 24+ | with Compose V2 plugin — used to run the database |
| conda | any | used to create the Python environment |

**Python environment (conda):**

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

**Frontend dependencies:**

```bash
npm install --prefix frontend
```

### Environment variables

Copy `.env.example` and fill in values:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Docker Compose DB config |

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

### Tests

Requires a running PostgreSQL instance (a separate test database is created automatically).

```bash
conda activate COMP3011-Coursework-1
cd backend
python -m pytest
python -m pytest --cov=app --cov-report=term-missing   # with coverage
```

Target: 100% coverage.

## Production

Requires Docker 24+ with the Compose V2 plugin.

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
