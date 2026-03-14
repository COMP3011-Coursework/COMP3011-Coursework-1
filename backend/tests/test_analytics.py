"""Analytics endpoint tests.

These tests depend on `analytics_seed` — a session-scoped fixture in conftest.py
that inserts 2 countries × 3 commodities × 6 monthly price observations into a
dedicated connection (committed, not rolled back) so all tests in this module
can read from it.

The `client` fixture overrides get_db to use the per-test transaction-rollback
session. However, analytics tests don't write data — they only read the
session-scoped seed data that was committed directly to the test DB.
"""

import pytest
from httpx import AsyncClient


class TestTrends:
    async def test_returns_points(
        self, client: AsyncClient, analytics_seed
    ):
        country = analytics_seed["countries"][0]
        commodity_id = analytics_seed["commodity_ids"][0]
        resp = await client.get(
            f"/api/v1/analytics/trends?country={country}&commodity_id={commodity_id}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "points" in data
        assert len(data["points"]) > 0

    async def test_point_date_format(
        self, client: AsyncClient, analytics_seed
    ):
        country = analytics_seed["countries"][0]
        commodity_id = analytics_seed["commodity_ids"][0]
        resp = await client.get(
            f"/api/v1/analytics/trends?country={country}&commodity_id={commodity_id}"
        )
        points = resp.json()["points"]
        # Each date should be in YYYY-MM format
        for p in points:
            parts = p["date"].split("-")
            assert len(parts) == 2
            assert len(parts[0]) == 4  # year
            assert len(parts[1]) == 2  # month

    async def test_empty_for_unknown_country(
        self, client: AsyncClient, analytics_seed
    ):
        commodity_id = analytics_seed["commodity_ids"][0]
        resp = await client.get(
            f"/api/v1/analytics/trends?country=ZZZ&commodity_id={commodity_id}"
        )
        assert resp.status_code == 200
        assert resp.json()["points"] == []


class TestVolatility:
    async def test_returns_items(
        self, client: AsyncClient, analytics_seed
    ):
        country = analytics_seed["countries"][0]
        resp = await client.get(f"/api/v1/analytics/volatility?country={country}")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) > 0

    async def test_ordered_by_cv_desc(
        self, client: AsyncClient, analytics_seed
    ):
        country = analytics_seed["countries"][0]
        resp = await client.get(f"/api/v1/analytics/volatility?country={country}")
        items = resp.json()["items"]
        cvs = [i["cv"] for i in items]
        assert cvs == sorted(cvs, reverse=True)

    async def test_limit_respected(
        self, client: AsyncClient, analytics_seed
    ):
        country = analytics_seed["countries"][0]
        resp = await client.get(
            f"/api/v1/analytics/volatility?country={country}&limit=1"
        )
        assert len(resp.json()["items"]) <= 1


class TestRegionalComparison:
    async def test_returns_countries(
        self, client: AsyncClient, analytics_seed
    ):
        commodity_id = analytics_seed["commodity_ids"][0]
        resp = await client.get(
            f"/api/v1/analytics/regional-comparison?commodity_id={commodity_id}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "countries" in data
        assert len(data["countries"]) >= 2  # both AAA and BBB

    async def test_ordered_by_price_desc(
        self, client: AsyncClient, analytics_seed
    ):
        commodity_id = analytics_seed["commodity_ids"][0]
        resp = await client.get(
            f"/api/v1/analytics/regional-comparison?commodity_id={commodity_id}"
        )
        prices = [c["avg_usdprice"] for c in resp.json()["countries"]]
        assert prices == sorted(prices, reverse=True)


class TestCrisisScores:
    async def test_list_returns_scores(
        self, client: AsyncClient, analytics_seed
    ):
        resp = await client.get("/api/v1/analytics/crisis-scores")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_each_score_has_required_fields(
        self, client: AsyncClient, analytics_seed
    ):
        resp = await client.get("/api/v1/analytics/crisis-scores")
        for item in resp.json():
            assert "countryiso3" in item
            assert "crisis_score" in item
            assert "severity" in item
            assert item["severity"] in ("stable", "moderate", "high", "critical")
            assert 0 <= item["crisis_score"] <= 100

    async def test_by_country(
        self, client: AsyncClient, analytics_seed
    ):
        country = analytics_seed["countries"][0]
        resp = await client.get(f"/api/v1/analytics/crisis-scores/{country}")
        assert resp.status_code == 200
        assert resp.json()["countryiso3"] == country

    async def test_by_country_not_found(
        self, client: AsyncClient, analytics_seed
    ):
        resp = await client.get("/api/v1/analytics/crisis-scores/ZZZ")
        assert resp.status_code == 404


class TestMarketSummary:
    async def test_market_summary(
        self, client: AsyncClient, analytics_seed
    ):
        market_id = analytics_seed["market_ids"][0]
        resp = await client.get(f"/api/v1/analytics/markets/{market_id}/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["market_id"] == market_id
        assert "market_name" in data
        assert data["total_prices"] > 0
        assert data["commodity_count"] >= 1

    async def test_market_summary_not_found(
        self, client: AsyncClient, analytics_seed
    ):
        resp = await client.get("/api/v1/analytics/markets/999999/summary")
        assert resp.status_code == 404
