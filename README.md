# Global Food Price Monitor

A full-stack web application for visualising and analysing global food prices using
[World Food Programme (WFP)](https://data.humdata.org/dataset/wfp-food-prices) data.

Built for COMP3011 Web Services and Web Data — University of Leeds, 2025/26.

**Stack:** FastAPI · PostgreSQL · React · Vite · TypeScript · Tailwind CSS · Docker

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose v2)
- Git

### 1. Clone the repository

```bash
git clone <repo-url>
cd COMP3011-Coursework-1
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY`. The defaults work for local development.

### 3. Add data files

Place the WFP CSV files in a `data/` directory at the repo root:

```text
data/
  wfp_commodities_global.csv
  wfp_currencies_global.csv
  wfp_markets_global.csv
  wfp_food_prices_2020.csv
  wfp_food_prices_2021.csv
  ...
```

### 4. Start the full stack

```bash
docker compose up --build
```

| Service  | URL                                       |
|----------|-------------------------------------------|
| Frontend | <http://localhost:5173>                   |
| Backend  | <http://localhost:8000>                   |
| API docs | <http://localhost:8000/docs>              |
| ReDoc    | <http://localhost:8000/redoc>             |
| MCP      | <http://localhost:3000/sse>               |

### 5. Seed the database

Once the stack is running (first time only):

```bash
docker compose exec backend python scripts/seed.py
```

This imports all CSV data and creates an `admin` user (password: `admin123`).

---

## Environment Variables

| Variable            | Description                               | Example                                              |
|---------------------|-------------------------------------------|------------------------------------------------------|
| `DATABASE_URL`      | Async SQLAlchemy connection string        | `postgresql+psycopg://user:pass@db:5432/foodpricedb` |
| `SECRET_KEY`        | JWT signing secret (change in production) | `a-long-random-string`                               |
| `POSTGRES_DB`       | PostgreSQL database name                  | `foodpricedb`                                        |
| `POSTGRES_USER`     | PostgreSQL username                       | `foodprice`                                          |
| `POSTGRES_PASSWORD` | PostgreSQL password                       | `foodprice123`                                       |
| `CORS_ORIGINS`      | Comma-separated allowed CORS origins      | `http://localhost:5173,http://localhost:3000`        |
| `VITE_API_URL`      | Backend API base URL for the frontend     | `http://localhost:8000`                              |

---

## Running Tests

```bash
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

---

## Database Migrations

Generate a new migration after changing models:

```bash
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head
```

---

## MCP Server (Claude Desktop)

The MCP server exposes food price tools to AI assistants via the
[Model Context Protocol](https://modelcontextprotocol.io/).

Add the following to your Claude Desktop config
(`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "food-price-monitor": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

Available tools:

- `get_global_crisis_overview` — Top 20 countries by food crisis score
- `get_crisis_summary(country)` — Full crisis breakdown for a country
- `get_price_trends(country, commodity, months)` — USD price time series
- `compare_regional_prices(commodity)` — Cross-country price comparison
- `get_volatile_commodities(country, limit)` — Most volatile commodities

---

## Project Structure

```text
COMP3011-Coursework-1/
├── backend/           FastAPI application
│   ├── app/           Application code (models, routers, services)
│   ├── alembic/       Database migrations
│   └── scripts/       Utility scripts (seed.py)
├── frontend/          React + Vite + TypeScript application
├── mcp-server/        FastMCP server
├── docs/              Design documents and GenAI logs
└── docker-compose.yml Full stack orchestration
```

---

## API Documentation

- Interactive (Swagger UI): <http://localhost:8000/docs>
- Read-only reference (ReDoc): <http://localhost:8000/redoc>

A PDF export of the API documentation is submitted separately via Minerva.

---

## Deployment

### Local / Self-hosted

`docker compose up` is the primary deployment method. All services run in Docker containers.

### Frontend on Vercel (optional)

1. Build the frontend: `cd frontend && npm run build`
2. Deploy `dist/` to Vercel
3. Set `VITE_API_URL` to your backend's public URL in Vercel environment settings
