"""Tests for MCP tool functions (app/mcp/tools.py)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.analytics import (
    CrisisScoreResponse,
    RegionalComparisonResponse,
    RegionalItem,
    TrendPoint,
    TrendResponse,
    VolatilityItem,
    VolatilityResponse,
)


def _make_db_mock():
    """Return a mock (session_local, db_session) pair for AsyncSessionLocal()."""
    mock_db = AsyncMock()
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_db)
    mock_cm.__aexit__ = AsyncMock(return_value=False)
    mock_session_local = MagicMock(return_value=mock_cm)
    return mock_session_local, mock_db


class TestCommodityIdHelper:
    async def test_found(self):
        from app.mcp.tools import _commodity_id

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1001
        mock_db.execute = AsyncMock(return_value=mock_result)

        cid = await _commodity_id(mock_db, "Rice")
        assert cid == 1001

    async def test_not_found_raises(self):
        from app.mcp.tools import _commodity_id

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="not found"):
            await _commodity_id(mock_db, "UnknownCrop")


class TestGetGlobalCrisisOverview:
    async def test_returns_list_of_dicts(self):
        from app.mcp.tools import get_global_crisis_overview

        mock_session_local, _ = _make_db_mock()
        mock_scores = [
            CrisisScoreResponse(
                countryiso3="ETH", crisis_score=80.0, severity="critical",
                volatility_score=70.0, trend_score=75.0, breadth_score=85.0,
            )
        ]

        with patch("app.mcp.tools.AsyncSessionLocal", mock_session_local), \
             patch("app.mcp.tools.compute_crisis_scores", AsyncMock(return_value=mock_scores)):
            result = await get_global_crisis_overview()

        assert len(result) == 1
        assert result[0]["countryiso3"] == "ETH"
        assert result[0]["severity"] == "critical"


class TestGetCrisisSummary:
    async def test_returns_summary_dict(self):
        from app.mcp.tools import get_crisis_summary

        mock_session_local, _ = _make_db_mock()
        mock_score = CrisisScoreResponse(
            countryiso3="KEN", crisis_score=40.0, severity="moderate",
            volatility_score=30.0, trend_score=35.0, breadth_score=50.0,
        )
        mock_volatility = VolatilityResponse(
            country="KEN",
            items=[VolatilityItem(commodity_id=1, commodity_name="Rice", cv=0.2, avg_usdprice=1.5)],
        )

        with patch("app.mcp.tools.AsyncSessionLocal", mock_session_local), \
             patch("app.mcp.tools.compute_crisis_scores", AsyncMock(return_value=[mock_score])), \
             patch("app.mcp.tools.analytics_service.get_volatility", AsyncMock(return_value=mock_volatility)):
            result = await get_crisis_summary("KEN")

        assert result["countryiso3"] == "KEN"
        assert len(result["top_volatile_commodities"]) == 1

    async def test_raises_when_no_data(self):
        from app.mcp.tools import get_crisis_summary

        mock_session_local, _ = _make_db_mock()

        with patch("app.mcp.tools.AsyncSessionLocal", mock_session_local), \
             patch("app.mcp.tools.compute_crisis_scores", AsyncMock(return_value=[])):
            with pytest.raises(ValueError, match="No data found"):
                await get_crisis_summary("ZZZ")


class TestGetPriceTrendsMcp:
    async def test_returns_list_of_points(self):
        from app.mcp.tools import get_price_trends

        mock_session_local, mock_db = _make_db_mock()
        mock_scalar_result = MagicMock()
        mock_scalar_result.scalar.return_value = 1001
        mock_db.execute = AsyncMock(return_value=mock_scalar_result)

        mock_trends = TrendResponse(
            country="KEN", commodity_id=1001,
            points=[TrendPoint(date="2025-01", avg_usdprice=2.5, count=3)],
        )

        with patch("app.mcp.tools.AsyncSessionLocal", mock_session_local), \
             patch("app.mcp.tools.analytics_service.get_price_trends", AsyncMock(return_value=mock_trends)):
            result = await get_price_trends("KEN", "Rice", months=12)

        assert len(result) == 1
        assert result[0]["date"] == "2025-01"
        assert result[0]["avg_usdprice"] == pytest.approx(2.5)


class TestCompareRegionalPrices:
    async def test_returns_list_of_countries(self):
        from app.mcp.tools import compare_regional_prices

        mock_session_local, mock_db = _make_db_mock()
        mock_scalar_result = MagicMock()
        mock_scalar_result.scalar.return_value = 1001
        mock_db.execute = AsyncMock(return_value=mock_scalar_result)

        mock_comparison = RegionalComparisonResponse(
            commodity_id=1001,
            countries=[
                RegionalItem(countryiso3="ETH", avg_usdprice=1.2, count=5),
                RegionalItem(countryiso3="KEN", avg_usdprice=1.0, count=4),
            ],
        )

        with patch("app.mcp.tools.AsyncSessionLocal", mock_session_local), \
             patch("app.mcp.tools.analytics_service.get_regional_comparison", AsyncMock(return_value=mock_comparison)):
            result = await compare_regional_prices("Rice")

        assert len(result) == 2
        assert result[0]["countryiso3"] == "ETH"


class TestGetVolatileCommodities:
    async def test_returns_list_and_clamps_limit(self):
        from app.mcp.tools import get_volatile_commodities

        mock_session_local, _ = _make_db_mock()
        mock_volatility = VolatilityResponse(
            country="SOM",
            items=[
                VolatilityItem(commodity_id=1, commodity_name="Maize", cv=0.5, avg_usdprice=0.8),
            ],
        )

        # limit=100 should be clamped to 50
        with patch("app.mcp.tools.AsyncSessionLocal", mock_session_local), \
             patch("app.mcp.tools.analytics_service.get_volatility", AsyncMock(return_value=mock_volatility)) as mock_get_vol:
            result = await get_volatile_commodities("SOM", limit=100)

        assert len(result) == 1
        assert result[0]["commodity_name"] == "Maize"
        # Verify limit was clamped to 50
        mock_get_vol.assert_called_once()
        called_limit = mock_get_vol.call_args[0][2]
        assert called_limit == 50
