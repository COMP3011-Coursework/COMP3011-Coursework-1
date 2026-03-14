import pytest
from httpx import AsyncClient

from tests.conftest import price_payload


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "newuser", "email": "new@example.com", "password": "secret123"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "testuser", "email": "other@example.com", "password": "pw"},
        )
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "otheruser", "email": "test@example.com", "password": "pw"},
        )
        assert resp.status_code == 400


class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        _, plain = test_user
        resp = await client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": plain},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        resp = await client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_user(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            data={"username": "nobody", "password": "anything"},
        )
        assert resp.status_code == 401


class TestProtectedEndpoints:
    async def test_create_price_requires_auth(
        self, client: AsyncClient, commodity, market, currency
    ):
        resp = await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id),
        )
        assert resp.status_code == 401

    async def test_delete_price_requires_auth(
        self, client: AsyncClient, commodity, market, currency, auth_headers
    ):
        # Create via authenticated request
        create_resp = await client.post(
            "/api/v1/prices",
            json=price_payload(commodity.id, market.id),
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        price_id = create_resp.json()["id"]

        # Attempt to delete without token
        del_resp = await client.delete(f"/api/v1/prices/{price_id}")
        assert del_resp.status_code == 401
