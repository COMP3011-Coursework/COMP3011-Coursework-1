from datetime import date

import pytest
from httpx import AsyncClient

from tests.conftest import price_payload


class TestCreatePrice:
    async def test_create_success(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        resp = await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id, usdprice=2.50),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["countryiso3"] == "TST"
        assert data["usdprice"] == pytest.approx(2.50)

    async def test_create_missing_required_field(
        self, client: AsyncClient, auth_headers
    ):
        resp = await client.post(
            "/api/v1/prices",
            json={"countryiso3": "TST"},  # missing many required fields
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestGetPrice:
    async def test_get_by_id(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        create = await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id),
            headers=auth_headers,
        )
        price_id = create.json()["id"]

        resp = await client.get(f"/api/v1/prices/{price_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == price_id

    async def test_get_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/prices/999999")
        assert resp.status_code == 404


class TestListPrices:
    async def test_list_returns_items(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        for _ in range(3):
            await client.post(
                "/api/v1/prices",
                json=price_payload(commodity.id, market.id),
                headers=auth_headers,
            )

        resp = await client.get("/api/v1/prices")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 3

    async def test_filter_by_country(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id, country="TST"),
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id, country="XYZ"),
            headers=auth_headers,
        )

        resp = await client.get("/api/v1/prices?country=TST")
        data = resp.json()
        assert all(item["countryiso3"] == "TST" for item in data["items"])

    async def test_pagination(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        # Insert 5 entries
        for i in range(5):
            await client.post(
                "/api/v1/prices",
                json=price_payload(
                    commodity.id, market.id, usdprice=float(i + 1)
                ),
                headers=auth_headers,
            )

        resp = await client.get(
            f"/api/v1/prices?country=TST&commodity_id={commodity.id}&page=1&page_size=2"
        )
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5
        assert data["page"] == 1
        assert data["page_size"] == 2

    async def test_filter_by_market_id(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id),
            headers=auth_headers,
        )
        resp = await client.get(f"/api/v1/prices?market_id={market.id}")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    async def test_filter_by_date_range(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        from datetime import timedelta
        today = date.today()
        await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id),
            headers=auth_headers,
        )
        resp = await client.get(
            f"/api/v1/prices"
            f"?date_from={today - timedelta(days=1)}&date_to={today + timedelta(days=1)}"
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


class TestUpdatePrice:
    async def test_update_usdprice(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        create = await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id, usdprice=1.00),
            headers=auth_headers,
        )
        price_id = create.json()["id"]

        resp = await client.put(
            f"/api/v1/prices/{price_id}",
            json={"usdprice": 9.99},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["usdprice"] == pytest.approx(9.99)

    async def test_update_not_found(self, client: AsyncClient, auth_headers):
        resp = await client.put(
            "/api/v1/prices/999999",
            json={"usdprice": 1.0},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestDeletePrice:
    async def test_delete_success(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        create = await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id),
            headers=auth_headers,
        )
        price_id = create.json()["id"]

        del_resp = await client.delete(
            f"/api/v1/prices/{price_id}", headers=auth_headers
        )
        assert del_resp.status_code == 204

        get_resp = await client.get(f"/api/v1/prices/{price_id}")
        assert get_resp.status_code == 404

    async def test_delete_not_found(self, client: AsyncClient, auth_headers):
        resp = await client.delete(
            "/api/v1/prices/999999", headers=auth_headers
        )
        assert resp.status_code == 404
