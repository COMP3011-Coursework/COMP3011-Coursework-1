<!-- markdownlint-disable MD024 -->
# Initial Design

## Tech Stack

- Frontend: React, Vite, TypeScript, Tailwind CSS, Leaflet.js, Chart.js
- Backend: Python 3.14, FastAPI, Pydantic
- Database: PostgreSQL, SQLAlchemy, Alembic
- Deployment: Docker, Docker Compose
- Testing: pytest, pytest-cov, FastAPI TestClient, httpx

## File Structure

- docs/
  - api-documentation.md
  - genai-logs/
  - plans/
    - 01-initial-design.md
    - ...other design docs
- backend/
- frontend/
- .env.example
- .gitignore
- docker-compose.yml
- README.md

## Features

### Project Overview

The Global Food Price Monitor is a data-driven web API and dashboard  built on the UN World Food Programme (WFP) food prices dataset, covering approximately 262,000 price observations across 105 countries, 1,154  commodities, and 10,549 markets. The system provides full CRUD  functionality for managing field price observations, alongside analytical  endpoints for trend analysis, price volatility, regional comparisons, and a composite crisis scoring algorithm. A React dashboard visualises crisis severity across a Leaflet choropleth world map, with interactive country detail panels showing price trends and volatility rankings. An MCP server exposes AI-callable tools enabling LLMs such as Claude to query the API intelligently using natural language. Authentication is handled via JWT with Bcrypt password hashing, protecting all write operations while keeping analytical endpoints publicly accessible.

### Data Management

- Submit new food price observations for any market and commodity
- View, edit, and delete existing price observations
- Filter observations by country, commodity, and date range

### Analytics

- View price trends over time for any country and commodity
- Identify the most price-volatile commodities in any country
- Compare prices for a commodity across countries
- Browse a global crisis severity ranking across all countries
- View a detailed crisis breakdown for a specific country
- Explore price activity and commodity coverage for any market

### Dashboard

- Interactive world map showing food crisis severity by country
- Click any country to view its crisis score, price trends, and most volatile commodities
- Explore and filter price observations with live chart updates

### AI Integration

- Ask Claude natural language questions about food prices and crisis conditions, answered by live API data

### Authentication

- Register and log in to access data management features
- Analytical data is publicly accessible without an account

### Backend

#### Dataset

Dataset from [Global - Food Prices](https://data.humdata.org/dataset/global-wfp-food-prices)

Dataset metadata: <https://data.humdata.org/dataset/31579af5-3895-4002-9ee3-c50857480785/download_metadata?format=json>

Dataset format:

**1. `wfp_food_prices_YYYY.csv`** *(year files — e.g. 1990, 2026)*

```text
countryiso3, date, admin1, admin2, market, market_id, latitude, 
longitude, category, commodity, commodity_id, unit, priceflag, 
pricetype, currency, price, usdprice
```

**2. `wfp_commodities_global.csv`**

```text
commodity_id, category, commodity
```

**3. `wfp_markets_global.csv`**

```text
market_id, market, countryiso3, admin1, admin2, latitude, longitude
```

**4. `wfp_currencies_global.csv`**

```text
code, name
```

#### Database

Seed data

- create an admin user
- import wfp_commodities_global.csv → commodities table
- import wfp_markets_global.csv → markets table
- import wfp_currencies_global.csv → currencies table
- import wfp_food_prices_*.csv → prices fact table

#### API Endpoints

```text
# CRUD
POST   /api/v1/prices
GET    /api/v1/prices
GET    /api/v1/prices/{id}
PUT    /api/v1/prices/{id}
DELETE /api/v1/prices/{id}

# Analytics
GET    /api/v1/analytics/trends
GET    /api/v1/analytics/volatility
GET    /api/v1/analytics/regional-comparison
GET    /api/v1/analytics/crisis-scores
GET    /api/v1/analytics/crisis-scores/{country}
GET    /api/v1/analytics/markets/{market_id}/summary

# Reference data (needed by frontend dropdowns)
GET    /api/v1/countries
GET    /api/v1/commodities
GET    /api/v1/markets

# Authentication
POST   /api/v1/auth/register
POST   /api/v1/auth/login
```

#### MCP Endpoints

```text
get_global_crisis_overview()         → best demo, no params needed
get_crisis_summary(country)          → single country deep dive  
get_price_trends(country, commodity) → trend over time
compare_regional_prices(commodity)   → cross-country comparison
get_volatile_commodities(country)    → volatility ranking
```

#### Authentication

Use Bcrypt for password hashing and JWT for token-based authentication with token expiry.

### Frontend

#### Pages

```text
/              → Dashboard (map + global overview)
/explorer      → Filter by country, commodity, date range
/data-entry    → CRUD interface for price observations
```

#### Dashboard Page (main view)

Two column layout — map left, detail panel right. Single column on mobile.

- **Leaflet choropleth map** — countries shaded by crisis score (green → yellow → orange → red)
- **Colour scale** — 0-25 stable, 25-50 moderate, 50-75 high, 75-100 critical
- **Click country** → opens detail panel
- **Legend** — visible below map

#### Country Detail Panel

Opens on country click. Three simultaneous API calls via `Promise.all`:

```text
1. Crisis score card     → /api/v1/analytics/crisis-scores/{country}
2. Price trend chart     → /api/v1/analytics/trends
3. Volatility rankings   → /api/v1/analytics/volatility
```

Panel contains:

- Country name, flag, crisis score, severity badge
- Chart.js line chart (price trend, commodity selector dropdown)
- Top 3 most volatile commodities list
- Contributing factors progress bars (volatility, price trend, baseline deviation)

#### Explorer Page

- Filter controls — country, commodity, date range
- Results table — paginated price observations
- Chart.js line chart — updates on filter change
- Feeds from `/api/v1/analytics/trends` and `/api/v1/prices`

#### Data Entry Page

- Create form — submit new price observation
- Edit/delete controls on existing records
- Requires JWT authentication
- Feeds CRUD endpoints

#### GeoJSON

```text
/frontend/public/data/world.geojson
```

Loaded once on page init. Country boundaries joined to crisis scores by ISO country code client-side.

#### Responsive behaviour

- Desktop — two column (map + panel side by side)
- Mobile — single column, detail panel slides up from bottom
- Tailwind `md:grid-cols-2` handles breakpoint

## Claude Code Dialog

Write a Python script that exports Claude Code conversation logs to Markdown files for GenAI declaration purposes.

Requirements:

- Read conversation logs from Claude Code's local storage
- Export each conversation as a separate Markdown file
- Include timestamps, prompts, and responses
- Save output to docs/genai-logs/. Create a README file in this directory for index and online GenAI share links.
