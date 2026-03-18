# Database Schema

The database uses PostgreSQL with five tables. `prices` is the central fact table; `markets`, `commodities`, and `currencies` are reference/dimension tables; `users` supports authentication.

## Entity Relationship Diagram

```mermaid
erDiagram
  prices {
    serial id PK
    date date
    char countryiso3
    varchar admin1
    varchar admin2
    integer market_id FK
    integer commodity_id FK
    varchar category
    varchar unit
    varchar priceflag
    varchar pricetype
    varchar currency_code FK
    numeric price
    numeric usdprice
    timestamp created_at
    timestamp updated_at
  }
  markets {
    integer id PK
    varchar name
    char countryiso3
    varchar admin1
    varchar admin2
    float latitude
    float longitude
  }
  commodities {
    integer id PK
    varchar category
    varchar name
  }
  currencies {
    varchar code PK
    varchar name
  }
  users {
    serial id PK
    varchar username
    varchar email
    varchar hashed_password
    timestamp created_at
  }
  prices }o--|| markets : "market_id"
  prices }o--|| commodities : "commodity_id"
  prices }o--|| currencies : "currency_code"
```

## Notes

- `prices.usdprice` is pre-computed at insert time to avoid repeated currency conversion at query time.
- Three composite indexes on `prices` target the most common analytical access patterns:
  - `(countryiso3, date)` — country-level time-series queries
  - `(commodity_id, date)` — commodity-level trend queries
  - `(market_id)` — market summary queries
- `users` is not linked to `prices`; it exists solely for JWT authentication.
