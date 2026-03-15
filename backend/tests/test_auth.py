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

    async def test_invalid_token_returns_401(self, client: AsyncClient):
        resp = await client.delete(
            "/api/v1/prices/99999",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert resp.status_code == 401

    async def test_token_without_sub_returns_401(self, client: AsyncClient):
        from app.auth.jwt import create_access_token
        token = create_access_token({"no_sub": "value"})
        resp = await client.delete(
            "/api/v1/prices/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    async def test_token_unknown_user_returns_401(self, client: AsyncClient):
        from app.auth.jwt import create_access_token
        token = create_access_token({"sub": "ghost_user_not_in_db"})
        resp = await client.delete(
            "/api/v1/prices/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    async def test_inactive_user_returns_403(
        self, client: AsyncClient, db, auth_headers, test_user
    ):
        from sqlalchemy import select
        from app.models.user import User
        user, _ = test_user
        result = await db.execute(select(User).where(User.id == user.id))
        db_user = result.scalars().first()
        db_user.is_active = False
        await db.flush()
        resp = await client.delete(
            "/api/v1/prices/99999",
            headers=auth_headers,
        )
        assert resp.status_code == 403
