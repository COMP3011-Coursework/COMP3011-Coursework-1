# API Reference

Interactive docs at `/docs` (Swagger UI) and `/redoc`.

## Authentication

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/v1/auth/register` | POST | Create account |
| `/api/v1/auth/login` | POST | Login, returns JWT |

A default admin account is created automatically on first boot:

| Field | Value |
| --- | --- |
| Username | `admin` |
| Password | `admin123` |

## Prices

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/api/v1/prices` | GET | — | List prices (filters: country, commodity_id, market_id, date_from, date_to, page, page_size) |
| `/api/v1/prices` | POST | ✓ | Create price record |
| `/api/v1/prices/{id}` | GET | — | Get single price |
| `/api/v1/prices/{id}` | PUT | ✓ | Update price |
| `/api/v1/prices/{id}` | DELETE | ✓ | Delete price |

## Analytics

| Endpoint | Description |
| --- | --- |
| `GET /api/v1/analytics/trends?country=&commodity_id=` | Monthly avg price time series |
| `GET /api/v1/analytics/volatility?country=` | Commodities ranked by price volatility (CoV) |
| `GET /api/v1/analytics/regional-comparison?commodity_id=` | Avg price per country |
| `GET /api/v1/analytics/crisis-scores` | All countries ranked by crisis score |
| `GET /api/v1/analytics/crisis-scores/{country}` | Single-country crisis breakdown |
| `GET /api/v1/analytics/markets/{market_id}/summary` | Market statistics |

## Reference data

| Endpoint | Description |
| --- | --- |
| `GET /api/v1/countries` | Countries with price data |
| `GET /api/v1/commodities` | All commodities |
| `GET /api/v1/markets?country=` | Markets (optionally filtered by country) |
