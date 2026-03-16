# Analytics

The analytics module provides five features under `/api/v1/analytics/`. All queries operate on the `prices` table, which is indexed on `(countryiso3, date)`, `(commodity_id, date)`, and `market_id` for performance.

---

## Price trends

Returns a monthly average price time series for one country/commodity pair. Prices are grouped by `YYYY-MM` and averaged; null prices are excluded. Supports optional `date_from` / `date_to` filtering.

---

## Commodity volatility

Ranks commodities within a country by price volatility using the **Coefficient of Variation (CV)**:

```text
CV = stddev(price) / avg(price)
```

CV is scale-independent, so commodities priced in different units can be compared directly. Results are sorted descending; `limit` caps the list (default 10, max 50).

---

## Regional comparison

Compares the average USD price of one commodity across all countries that have recorded it. Supports optional `date_from` / `date_to` filtering. Results are sorted by average price descending.

---

## Market summary

Provides an overview of a single market: total price records, date span, number of distinct commodities, and the latest recorded price per commodity (resolved with a `MAX(date)` subquery per commodity).

---

## Crisis scores

Produces a composite food-crisis indicator for every country in the dataset. The score is built from three components, each computed over a **trailing 12-month window** ending at the country's own most-recent data date:

| Component | Weight | Measures |
| --- | --- | --- |
| Volatility | 40% | Average CV across commodities (≥ 3 observations required) |
| Trend | 35% | Latest 3-month avg vs 12-month avg — positive = prices rising |
| Breadth | 25% | Fraction of commodities whose latest price exceeds their trailing mean |

### Formula

```text
volatility = avg(stddev/mean) per commodity over trailing 12 months
trend      = (latest 3-month avg) / (trailing 12-month avg) − 1
breadth    = fraction of commodities with latest price > trailing mean

Each component min-max normalised across all countries.
crisis_score = (0.40 × vol + 0.35 × trend + 0.25 × breadth) × 100
```

All three components are min-max normalised across countries before being combined, so the score reflects a country's position relative to others in the current dataset rather than an absolute threshold.

### Severity bands

| Score | Severity |
| --- | --- |
| 0–25 | Stable |
| 25–50 | Moderate |
| 50–75 | High |
| 75–100 | Critical |

### Map coverage note

The choropleth map shows only the ~99 countries monitored by WFP. Developed nations (USA, UK, EU, Australia, etc.) are not tracked by WFP and will always appear gray — this reflects the source data.
