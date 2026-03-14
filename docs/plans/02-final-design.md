<!-- markdownlint-disable MD024 -->
# Final Design — COMP3011 Coursework 1

**Project:** Global Food Price Monitor
**Stack:** FastAPI · PostgreSQL · React · Docker
---

## 1. Decisions from Initial Design (Confirmed)

| Decision | Rationale |
|---|---|
| FastAPI + Pydantic | Auto-generates OpenAPI/Swagger docs; async support; modern Python |
| PostgreSQL + SQLAlchemy + Alembic | SQL required; Alembic gives version-controlled migrations |
| React + Vite + TypeScript + Tailwind | Fast DX; type safety; utility-first CSS |
| Leaflet.js choropleth map | Lightweight; well-documented; works with GeoJSON |
| Chart.js | Simple, reactive charts; good React integration |
| JWT + Bcrypt authentication | Industry-standard; protects write operations only |
| Docker Compose | Reproducible local dev; single `docker compose up` |
| MCP server | Required for 70-79 grade band |

## 2. Resolved Design Questions

### Python version
Use **Python 3.14** throughout — in the backend Docker image and the local conda env
`COMP3011-Coursework-1`. Use `psycopg[binary]` (psycopg3) instead of psycopg2 to avoid
C-extension wheel gaps on 3.14.

### Database: PostgreSQL (not SQLite)
PostgreSQL is retained. Primary deployment is self-hosted via Docker Compose. Vercel may
optionally host the frontend static build; the backend remains Docker-only.

### Deployment strategy

- **Primary**: Self-hosted Docker Compose (`docker compose up`) — full stack in one command
- **Frontend (optional)**: Vercel — connects to the self-hosted backend API via env var `VITE_API_URL`
- No `render.yaml` needed; deployment is Docker-first

### Crisis score algorithm (defined)
Score is computed per country over the trailing 12 months of data:

```
crisis_score = (
    0.40 × volatility_component +    # normalised coefficient of variation across commodities
    0.35 × trend_component +          # % price increase vs 12-month-ago baseline
    0.25 × breadth_component          # fraction of commodities with prices above 1-year mean
) × 100
```

Each component is min-max normalised across all countries before weighting, producing a
0–100 score. Thresholds: 0-25 stable, 25-50 moderate, 50-75 high, 75-100 critical.

### GeoJSON source
Natural Earth `ne_110m_admin_0_countries.geojson` (public domain). Downloaded once and
committed to `frontend/public/data/world.geojson`. Countries joined to crisis scores
client-side via `ISO_A3` property.

### MCP server implementation
**FastMCP** is mounted directly inside the FastAPI app as an ASGI sub-application at `/mcp`.
Tools live in `backend/app/mcp/tools.py` and call the service layer directly. No separate
container — one less Dockerfile, one less Docker service.

### API documentation export
FastAPI auto-generates two UIs from the OpenAPI spec:

- `/docs` — interactive Swagger UI (try-it-out buttons)
- `/redoc` — clean read-only reference page (better for printing to PDF)

PDF produced manually from `/redoc`. Submitted via Minerva alongside the technical report;
README links to it.

---

## 3. Finalized File Structure

```
COMP3011-Coursework-1/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app factory
│   │   ├── config.py                # Settings via pydantic-settings
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── price.py             # Price fact table
│   │   │   ├── commodity.py
│   │   │   ├── market.py
│   │   │   ├── currency.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── price.py             # Pydantic request/response schemas
│   │   │   ├── analytics.py
│   │   │   └── auth.py
│   │   ├── routers/
│   │   │   ├── prices.py            # CRUD
│   │   │   ├── analytics.py         # Analytics endpoints
│   │   │   ├── reference.py         # Countries, commodities, markets
│   │   │   └── auth.py              # Register, login
│   │   ├── services/
│   │   │   ├── analytics.py         # Business logic for analytics queries
│   │   │   └── crisis_score.py      # Crisis scoring algorithm
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   └── tools.py             # FastMCP tools mounted at /mcp
│   │   └── auth/
│   │       ├── jwt.py               # Token creation/verification
│   │       └── dependencies.py      # FastAPI auth dependencies
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── scripts/
│   │   └── seed.py                  # Import CSVs → database
│   ├── tests/
│   │   ├── conftest.py              # Test DB setup, fixtures
│   │   ├── test_prices.py
│   │   ├── test_analytics.py
│   │   └── test_auth.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── public/
│   │   └── data/
│   │       └── world.geojson
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx        # Map + detail panel
│   │   │   ├── Explorer.tsx         # Filter + table + chart
│   │   │   └── DataEntry.tsx        # CRUD forms
│   │   ├── components/
│   │   │   ├── ChoroplethMap.tsx
│   │   │   ├── CountryDetailPanel.tsx
│   │   │   ├── PriceTrendChart.tsx
│   │   │   ├── VolatilityList.tsx
│   │   │   ├── CrisisScoreCard.tsx
│   │   │   ├── PriceTable.tsx
│   │   │   └── NavBar.tsx
│   │   ├── hooks/
│   │   │   ├── useApi.ts            # Generic fetch wrapper
│   │   │   └── useAuth.ts           # JWT storage + auth state
│   │   ├── api/
│   │   │   ├── client.ts            # Fetch API instance + interceptors
│   │   │   ├── prices.ts
│   │   │   ├── analytics.ts
│   │   │   └── auth.ts
│   │   └── types/
│   │       └── index.ts             # Shared TypeScript types
│   ├── Dockerfile
│   ├── nginx.conf                   # Prod static serving + API proxy
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── genai-logs/
│   │   ├── README.md                # Index of exported logs
│   │   └── *.md                     # Per-session exported logs
│   └── plans/
│       ├── 01-initial-design.md
│       └── 02-final-design.md
├── scripts/
│   └── export_claude_logs.py        # Export Claude Code logs to Markdown
├── .env.example
├── .gitignore
├── docker-compose.yml               # Full stack: db + backend + frontend + mcp
└── README.md
```

---

## 4. Database Schema

### `commodities`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | = commodity_id from CSV |
| category | VARCHAR(100) | |
| name | VARCHAR(200) | |

### `markets`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | = market_id from CSV |
| name | VARCHAR(200) | |
| countryiso3 | CHAR(3) | FK index |
| admin1 | VARCHAR(200) | |
| admin2 | VARCHAR(200) | |
| latitude | FLOAT | |
| longitude | FLOAT | |

### `currencies`
| Column | Type | Notes |
|---|---|---|
| code | VARCHAR(10) PK | |
| name | VARCHAR(100) | |

### `prices`
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| date | DATE | Indexed |
| countryiso3 | CHAR(3) | Indexed |
| admin1 | VARCHAR(200) | |
| admin2 | VARCHAR(200) | |
| market_id | INTEGER FK → markets | Indexed |
| commodity_id | INTEGER FK → commodities | Indexed |
| category | VARCHAR(100) | |
| unit | VARCHAR(50) | |
| priceflag | VARCHAR(20) | |
| pricetype | VARCHAR(20) | |
| currency_code | VARCHAR(10) FK → currencies | |
| price | NUMERIC(12,4) | |
| usdprice | NUMERIC(12,4) | |
| created_at | TIMESTAMP | default now() |
| updated_at | TIMESTAMP | default now(), on update |

### `users`
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| username | VARCHAR(100) UNIQUE | |
| email | VARCHAR(200) UNIQUE | |
| hashed_password | VARCHAR(200) | Bcrypt |
| is_active | BOOLEAN | default true |
| created_at | TIMESTAMP | |

**Indexes:** `prices(countryiso3, date)`, `prices(commodity_id, date)`, `prices(market_id)`

---

## 5. API Endpoints (Finalized)

### CRUD — Prices

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/prices` | Required | Create price observation |
| GET | `/api/v1/prices` | No | List prices (paginated, filterable) |
| GET | `/api/v1/prices/{id}` | No | Get single price observation |
| PUT | `/api/v1/prices/{id}` | Required | Update price observation |
| DELETE | `/api/v1/prices/{id}` | Required | Delete price observation |

**Query params for GET /prices:** `country`, `commodity_id`, `market_id`, `date_from`, `date_to`, `page` (default 1), `page_size` (default 50, max 200)

### Analytics

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/analytics/trends` | No | Price trend over time |
| GET | `/api/v1/analytics/volatility` | No | Most volatile commodities in country |
| GET | `/api/v1/analytics/regional-comparison` | No | Cross-country price comparison |
| GET | `/api/v1/analytics/crisis-scores` | No | Global crisis ranking |
| GET | `/api/v1/analytics/crisis-scores/{country}` | No | Country crisis breakdown |
| GET | `/api/v1/analytics/markets/{market_id}/summary` | No | Market activity summary |

**Query params:**
- `trends`: `country` (required), `commodity_id` (required), `date_from`, `date_to`
- `volatility`: `country` (required), `limit` (default 10)
- `regional-comparison`: `commodity_id` (required), `date_from`, `date_to`
- `crisis-scores`: `limit` (default 50)

### Reference Data

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/countries` | No | List all countries (iso3, name) |
| GET | `/api/v1/commodities` | No | List all commodities |
| GET | `/api/v1/markets` | No | List markets (filterable by country) |

### Authentication

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` | No | Register user |
| POST | `/api/v1/auth/login` | No | Login, returns JWT |

### Error responses
All errors return `{"detail": "<message>"}` with appropriate HTTP status codes:
`400` Bad Request, `401` Unauthorized, `403` Forbidden, `404` Not Found, `422` Validation Error, `500` Internal Server Error

---

## 6. MCP Server Tools

Implemented via **FastMCP**. Each tool calls the shared service layer directly.

```python
get_global_crisis_overview()
# Returns top 20 crisis countries with scores, ranked. Best demo tool.

get_crisis_summary(country: str)
# Full crisis breakdown for one country: score, components, top volatile commodities

get_price_trends(country: str, commodity: str, months: int = 24)
# Time series of USD prices for a commodity in a country

compare_regional_prices(commodity: str)
# Latest prices for a commodity across all countries with data

get_volatile_commodities(country: str, limit: int = 10)
# Ranked list of most price-volatile commodities in a country
```

MCP is mounted in the FastAPI app at `/mcp` — accessible at `http://localhost:8000/mcp/sse`. Claude Desktop config provided in README.

---

## 7. Authentication Design

- **Registration**: POST `/auth/register` → hash password with bcrypt (12 rounds) → store user
- **Login**: POST `/auth/login` → verify password → return `{"access_token": "...", "token_type": "bearer"}`
- **Token**: JWT, signed with `SECRET_KEY` (env var), expiry = 24h, payload = `{"sub": username, "exp": ...}`
- **Protected routes**: FastAPI `Depends(get_current_user)` on POST/PUT/DELETE price endpoints
- **Public routes**: All GET and analytics endpoints — no auth required

---

## 8. Frontend Design

### Pages

**`/` — Dashboard**
- Two-column layout (map left, detail panel right). Mobile: single column.
- Leaflet choropleth: countries coloured by crisis score on load
- Click country → CountryDetailPanel opens with 3 concurrent API calls via `Promise.all`:
  1. `GET /analytics/crisis-scores/{country}`
  2. `GET /analytics/trends?country=...&commodity=<top commodity>`
  3. `GET /analytics/volatility?country=...`
- Detail panel: flag, crisis score badge, line chart, volatility list, factor bars

**`/explorer` — Price Explorer**
- Filter controls: country dropdown, commodity dropdown, date range pickers
- Paginated results table
- Line chart below, updates on filter change
- Data from `GET /prices` + `GET /analytics/trends`

**`/data-entry` — Data Management**
- Login/register form (if not authenticated)
- Create form: country, market, commodity, date, price, currency, unit
- Table of recent entries with Edit / Delete buttons
- Calls CRUD endpoints with JWT Bearer header

### State management
React Context for auth state (token, user). `useApi` hook wraps fetch with error handling. No Redux — overkill for this scope.

### Responsive behaviour
- Tailwind `md:grid-cols-2` splits map/panel on desktop
- Mobile: detail panel is a bottom sheet, map full-width

---

## 9. Testing Strategy

### Backend (pytest + httpx)

| Test file | Coverage |
|---|---|
| `test_auth.py` | Register, login, token expiry, unauthorized access |
| `test_prices.py` | Full CRUD, filtering, pagination, 404/422 error cases |
| `test_analytics.py` | trends, volatility, crisis-scores (known fixture data) |

**Test database**: Separate PostgreSQL DB (`test_db`) created in conftest.py fixture. Seeded with a small representative fixture dataset (~100 rows). Transactions rolled back between tests.

**Coverage target**: ≥80% on routers + services.

Run with: `pytest --cov=app --cov-report=term-missing`

---

## 10. Deployment

### Local development
```bash
docker compose up --build
# Backend:  http://localhost:8000
# Frontend: http://localhost:5173
# Docs:     http://localhost:8000/docs
# MCP:      http://localhost:8000/mcp/sse
```

### Self-hosted (production)
Same `docker-compose.yml` used on the host machine. Environment variables set via `.env` file.
Seed script runs once after first `docker compose up`.

### Frontend on Vercel (optional)
Build `frontend/` with `npm run build` and deploy `dist/` to Vercel.
Set `VITE_API_URL` to the backend's public URL in Vercel environment variables.

---

## 11. Deliverables Checklist

| Item | Notes |
|---|---|
| Public GitHub repo | Commit history shows incremental progress |
| README.md | Setup instructions, local + production, env vars, MCP config |
| API documentation PDF | Manually produced from `/redoc`; submitted separately via Minerva |
| Technical report (PDF, ≤5 pages) | Stack justification, architecture, testing, challenges, GenAI analysis |
| Presentation slides (PPTX) | Sections: version control, API docs, technical highlights, deliverables |
| GenAI declaration + logs | Claude Code session logs exported to `docs/genai-logs/` |

---

## 12. Implementation Phases

### Phase 1 — Infrastructure & Data Layer
1. Scaffold directory structure, `docker-compose.yml`, `Dockerfile`s
2. Configure `pydantic-settings`, `.env.example`, `.gitignore`
3. Define SQLAlchemy models + Alembic migrations
4. Write `scripts/seed.py` — import CSVs into PostgreSQL
5. Verify data loads correctly

### Phase 2 — Core API (CRUD + Auth)
1. Database session dependency
2. User model + Bcrypt + JWT utilities
3. `POST /auth/register` and `POST /auth/login`
4. Prices CRUD endpoints with validation and error codes
5. Reference data endpoints (countries, commodities, markets)
6. Pagination on `GET /prices`

### Phase 3 — Analytics Endpoints
1. `GET /analytics/trends`
2. `GET /analytics/volatility`
3. `GET /analytics/regional-comparison`
4. Crisis score algorithm + `GET /analytics/crisis-scores`
5. `GET /analytics/crisis-scores/{country}`
6. `GET /analytics/markets/{market_id}/summary`

### Phase 4 — MCP Server
1. Add FastMCP to `backend/requirements.txt`
2. Create `backend/app/mcp/tools.py` — implement 5 tools calling service layer
3. Mount at `/mcp` in `main.py` via `app.mount("/mcp", mcp.get_asgi_app())`
4. Test with Claude Desktop (`http://localhost:8000/mcp/sse`)

### Phase 5 — Frontend
1. Vite + React + TypeScript + Tailwind scaffold
2. Fetch API client, auth context, `useApi` hook
3. NavBar + routing
4. Dashboard page: Leaflet map + choropleth + CountryDetailPanel
5. Explorer page: filters + table + Chart.js
6. Data entry page: forms + CRUD

### Phase 6 — Testing & Documentation
1. pytest test suite (auth, CRUD, analytics)
2. Coverage report
3. README.md (setup, endpoints, screenshots)
4. Export Claude Code conversation logs

### Phase 7 — Deployment & Deliverables
1. Docker Compose production deploy (self-hosted)
2. Technical report (5 pages)
3. Presentation slides (PPTX)
4. Final submission to Minerva

---

## 13. Risk Register

| Risk | Mitigation |
|---|---|
| 262k row seed takes too long | Batch insert with `COPY` or `executemany`; use progress logging |
| GeoJSON ISO3 code mismatches | Build a small mapping dict for known exceptions (e.g. Kosovo `XKX`) |
| MCP server auth with Claude Desktop | Expose MCP without auth (read-only tools); write ops remain on main API |
