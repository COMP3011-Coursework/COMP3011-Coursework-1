"""Tests covering code paths not exercised by the main test suite.

Covers: health endpoint, get_db, _auto_seed, lifespan,
        _severity, _minmax_normalize, empty crisis scores.
"""

import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient


class TestHealthEndpoint:
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestDecodeToken:
    def test_invalid_token_returns_none(self):
        from app.auth.jwt import decode_access_token
        assert decode_access_token("bad.token.string") is None


class TestGetDb:
    async def test_commit_path(self):
        """Normal yield + resume → commit and close are called."""
        from app.database import get_db

        mock_session = AsyncMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        with patch("app.database.AsyncSessionLocal", return_value=mock_cm):
            gen = get_db()
            session = await gen.__anext__()
            assert session is mock_session
            with pytest.raises(StopAsyncIteration):
                await gen.__anext__()

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    async def test_rollback_path(self):
        """Exception thrown into generator → rollback and close are called."""
        from app.database import get_db

        mock_session = AsyncMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        with patch("app.database.AsyncSessionLocal", return_value=mock_cm):
            gen = get_db()
            await gen.__anext__()
            with pytest.raises(ValueError):
                await gen.athrow(ValueError("simulated error"))

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestAutoSeed:
    def _make_session_mock(self, count_value):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = count_value
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        mock_session_local = MagicMock(return_value=mock_cm)
        return mock_session, mock_session_local

    async def test_skips_when_db_populated(self):
        """_auto_seed returns early when commodities table is non-empty."""
        from app.main import _auto_seed

        mock_session, mock_session_local = self._make_session_mock(count_value=5)
        mock_loop = MagicMock()
        mock_loop.run_in_executor = AsyncMock(return_value=None)

        with patch("app.main.AsyncSessionLocal", mock_session_local), \
             patch("app.main.asyncio.get_event_loop", return_value=mock_loop), \
             patch("scripts.seed.download_missing"):
            await _auto_seed()

        # Only one execute call (the count check) — seeding functions not called
        mock_session.execute.assert_called_once()

    async def test_seeds_when_db_empty(self):
        """_auto_seed runs all seed functions when DB is empty."""
        from app.main import _auto_seed

        mock_session, mock_session_local = self._make_session_mock(count_value=0)
        mock_loop = MagicMock()
        mock_loop.run_in_executor = AsyncMock(return_value=None)

        mock_seed_commodities = AsyncMock()
        mock_seed_currencies = AsyncMock()
        mock_seed_markets = AsyncMock()
        mock_seed_prices = AsyncMock()
        mock_seed_admin = AsyncMock()

        with patch("app.main.AsyncSessionLocal", mock_session_local), \
             patch("app.main.asyncio.get_event_loop", return_value=mock_loop), \
             patch("scripts.seed.download_missing"), \
             patch("scripts.seed.seed_commodities", mock_seed_commodities), \
             patch("scripts.seed.seed_currencies", mock_seed_currencies), \
             patch("scripts.seed.seed_markets", mock_seed_markets), \
             patch("scripts.seed.seed_prices", mock_seed_prices), \
             patch("scripts.seed.seed_admin_user", mock_seed_admin):
            await _auto_seed()

        mock_seed_commodities.assert_called_once()
        mock_seed_admin.assert_called_once()


class TestLifespan:
    async def test_lifespan_runs_and_caches_countries(self):
        """lifespan creates tables, seeds DB, and caches WFP countries."""
        from app.main import lifespan, app as main_app
        from app import cache

        mock_conn = AsyncMock()
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = [("ETH",), ("KEN",)]
        mock_session.execute = AsyncMock(return_value=mock_result)

        @asynccontextmanager
        async def mock_engine_begin():
            yield mock_conn

        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        mock_session_local = MagicMock(return_value=mock_cm)

        with patch("app.main.engine") as mock_engine, \
             patch("app.main.AsyncSessionLocal", mock_session_local), \
             patch("app.main._auto_seed", AsyncMock()):
            mock_engine.begin = mock_engine_begin
            async with lifespan(main_app):
                pass

        assert "ETH" in cache.wfp_countries
        assert "KEN" in cache.wfp_countries


class TestSeverity:
    def test_moderate(self):
        from app.services.crisis_score import _severity
        assert _severity(25.0) == "moderate"
        assert _severity(49.9) == "moderate"

    def test_high(self):
        from app.services.crisis_score import _severity
        assert _severity(50.0) == "high"
        assert _severity(74.9) == "high"

    def test_critical(self):
        from app.services.crisis_score import _severity
        assert _severity(75.0) == "critical"
        assert _severity(100.0) == "critical"


class TestMinmaxNormalize:
    def test_empty_dict(self):
        from app.services.crisis_score import _minmax_normalize
        assert _minmax_normalize({}) == {}

    def test_all_same_value(self):
        from app.services.crisis_score import _minmax_normalize
        result = _minmax_normalize({"A": 3.0, "B": 3.0, "C": 3.0})
        assert result == {"A": 0.0, "B": 0.0, "C": 0.0}

    def test_different_values(self):
        from app.services.crisis_score import _minmax_normalize
        result = _minmax_normalize({"A": 0.0, "B": 1.0})
        assert result["A"] == pytest.approx(0.0)
        assert result["B"] == pytest.approx(1.0)


class TestCrisisScoreEmptyDb:
    async def test_returns_empty_list_when_no_data(self, client: AsyncClient):
        """compute_crisis_scores returns [] when prices table is empty."""
        from app.services.crisis_score import compute_crisis_scores
        from sqlalchemy.ext.asyncio import AsyncSession
        from unittest.mock import AsyncMock, MagicMock

        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)

        scores = await compute_crisis_scores(mock_db)
        assert scores == []
