from httpx import AsyncClient


class TestCountries:
    async def test_get_countries(self, client: AsyncClient, analytics_seed):
        resp = await client.get("/api/v1/countries")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        iso3s = [c["countryiso3"] for c in data]
        assert "AAA" in iso3s
        assert "BBB" in iso3s

    async def test_country_has_count(self, client: AsyncClient, analytics_seed):
        resp = await client.get("/api/v1/countries")
        for country in resp.json():
            assert "countryiso3" in country
            assert "count" in country
            assert country["count"] > 0


class TestCommodities:
    async def test_get_commodities(self, client: AsyncClient, analytics_seed):
        resp = await client.get("/api/v1/commodities")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    async def test_commodity_fields(self, client: AsyncClient, analytics_seed):
        resp = await client.get("/api/v1/commodities")
        for comm in resp.json():
            assert "id" in comm
            assert "name" in comm
            assert "category" in comm


class TestMarkets:
    async def test_get_markets(self, client: AsyncClient, analytics_seed):
        resp = await client.get("/api/v1/markets")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_filter_by_country(self, client: AsyncClient, analytics_seed):
        resp = await client.get("/api/v1/markets?country=AAA")
        assert resp.status_code == 200
        data = resp.json()
        assert all(m["countryiso3"] == "AAA" for m in data)
        assert len(data) >= 1

    async def test_market_fields(self, client: AsyncClient, analytics_seed):
        resp = await client.get("/api/v1/markets")
        for mkt in resp.json():
            assert "id" in mkt
            assert "name" in mkt
            assert "countryiso3" in mkt
