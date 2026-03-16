# Analytics

Five analytics features are available under `/api/v1/analytics/`. All queries run against the `prices` table, which is indexed on `(countryiso3, date)`, `(commodity_id, date)`, and `market_id` for performance.

---

## 1. Price trends

**Endpoint:** `GET /api/v1/analytics/trends`

**Parameters:** `country` (ISO3), `commodity_id`, optional `date_from` / `date_to`

Groups all prices for a country/commodity pair by calendar month (`YYYY-MM`) and returns the average USD price and observation count per month. Null prices are excluded. Useful for visualising how a commodity's price has evolved over time in a specific country.

---

## 2. Commodity volatility

**Endpoint:** `GET /api/v1/analytics/volatility`

**Parameters:** `country` (ISO3), optional `limit` (default 10, max 50)

Ranks commodities within a country by price volatility using the **Coefficient of Variation (CV)**:

```text
CV = stddev(price) / avg(price)
```

CV is scale-independent, making commodities with very different price levels directly comparable. Commodities with fewer than the minimum required observations are excluded. Results are sorted descending by CV.

---

## 3. Regional comparison

**Endpoint:** `GET /api/v1/analytics/regional-comparison`

**Parameters:** `commodity_id`, optional `date_from` / `date_to`

Returns the average USD price of a single commodity for every country that has recorded it, sorted by average price descending. Useful for identifying which regions face the highest food costs for a given commodity.

---

## 4. Market summary

**Endpoint:** `GET /api/v1/analytics/markets/{market_id}/summary`

Provides a snapshot of a single market:

- Total number of price records and the date range they span
- Count of distinct commodities tracked at the market
- Latest recorded price per commodity, resolved by taking the row with `MAX(date)` per commodity

---

## 5. Crisis scores

**Endpoints:** `GET /api/v1/analytics/crisis-scores`, `GET /api/v1/analytics/crisis-scores/{country}`

Produces a composite food-crisis indicator (0–100) for every country in the dataset, or for a single country. The score is built from three components, each computed over a **trailing 12-month window** ending at the country's own most-recent data date:

| Component | Weight | What it measures |
| --- | --- | --- |
| Volatility | 40% | Average CV across commodities (minimum 3 observations per commodity required) |
| Trend | 35% | Ratio of the latest 3-month average to the 12-month average, minus 1 — positive values indicate rising prices |
| Breadth | 25% | Fraction of commodities whose most recent price exceeds their 12-month trailing mean |

### Formula

```text
volatility = avg(stddev / mean) per commodity over trailing 12 months
trend      = (avg price in latest 3 months) / (avg price over 12 months) − 1
breadth    = fraction of commodities with latest price > trailing 12-month mean

Each component is min-max normalised across all countries in the dataset.
crisis_score = (0.40 × volatility + 0.35 × trend + 0.25 × breadth) × 100
```

Min-max normalisation means the score reflects a country's position **relative to others** in the current dataset, not an absolute threshold.

### Severity bands

| Score | Severity |
| --- | --- |
| 0–25 | Stable |
| 25–50 | Moderate |
| 50–75 | High |
| 75–100 | Critical |

### Map coverage note

The choropleth map covers only the ~99 countries monitored by WFP. Developed nations (USA, UK, EU, Australia, etc.) are not tracked by WFP and will always appear gray — this reflects the source data, not a gap in the application.
