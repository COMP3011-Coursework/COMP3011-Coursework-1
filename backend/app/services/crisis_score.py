from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import Price
from app.schemas.analytics import CrisisScoreResponse


def _severity(score: float) -> str:
    if score < 25:
        return "stable"
    elif score < 50:
        return "moderate"
    elif score < 75:
        return "high"
    return "critical"


def _minmax_normalize(values: dict[str, float]) -> dict[str, float]:
    if not values:
        return {}
    lo = min(values.values())
    hi = max(values.values())
    if hi == lo:
        return {k: 0.0 for k in values}
    return {k: (v - lo) / (hi - lo) for k, v in values.items()}


async def compute_crisis_scores(
    db: AsyncSession,
    country: str | None = None,
) -> list[CrisisScoreResponse]:
    """
    Compute crisis scores for all countries (or a single country).

    Components (all computed over trailing 12 months of data):
      volatility = coefficient of variation (stddev / avg usdprice) averaged across commodities
      trend      = (latest 3-month avg usdprice) / (prior 12-month avg) - 1
      breadth    = fraction of commodities where latest price > trailing 12-month mean

    Each component is min-max normalised across countries before weighting.
    crisis_score = (0.40 * vol + 0.35 * trend + 0.25 * breadth) * 100
    """

    # Step 1: compute raw components per country via SQL
    raw_sql = text("""
        WITH country_latest AS (
            -- per-country latest date so each country uses its own 12-month window
            SELECT countryiso3, MAX(date) AS max_date FROM prices GROUP BY countryiso3
        ),
        window_prices AS (
            SELECT
                p.countryiso3,
                p.commodity_id,
                p.usdprice,
                p.date,
                cl.max_date
            FROM prices p
            JOIN country_latest cl USING (countryiso3)
            WHERE p.usdprice IS NOT NULL
              AND p.date >= (cl.max_date - INTERVAL '12 months')
        ),
        volatility_cte AS (
            SELECT
                countryiso3,
                AVG(
                    CASE WHEN avg_price > 0
                         THEN stddev_price / avg_price
                         ELSE 0 END
                ) AS volatility
            FROM (
                SELECT
                    countryiso3,
                    commodity_id,
                    STDDEV(usdprice) AS stddev_price,
                    AVG(usdprice)    AS avg_price
                FROM window_prices
                GROUP BY countryiso3, commodity_id
                HAVING COUNT(*) >= 3
            ) sub
            GROUP BY countryiso3
        ),
        trend_cte AS (
            SELECT
                countryiso3,
                COALESCE(
                    (AVG(CASE WHEN date >= (max_date - INTERVAL '3 months')
                              THEN usdprice END)
                   / NULLIF(AVG(usdprice), 0)) - 1,
                    0
                ) AS trend
            FROM window_prices
            GROUP BY countryiso3
        ),
        breadth_cte AS (
            SELECT
                countryiso3,
                AVG(
                    CASE WHEN latest_price > trailing_mean THEN 1.0 ELSE 0.0 END
                ) AS breadth
            FROM (
                SELECT
                    countryiso3,
                    commodity_id,
                    AVG(usdprice) AS trailing_mean,
                    MAX(CASE WHEN date = max_date_per
                             THEN usdprice END) AS latest_price
                FROM (
                    SELECT
                        wp.*,
                        MAX(date) OVER (PARTITION BY countryiso3, commodity_id) AS max_date_per
                    FROM window_prices wp
                ) sub2
                GROUP BY countryiso3, commodity_id
            ) sub3
            GROUP BY countryiso3
        )
        SELECT
            t.countryiso3,
            COALESCE(v.volatility, 0) AS volatility,
            COALESCE(t.trend, 0)      AS trend,
            COALESCE(b.breadth, 0)    AS breadth
        FROM trend_cte t
        LEFT JOIN volatility_cte v USING (countryiso3)
        LEFT JOIN breadth_cte b USING (countryiso3)
        ORDER BY t.countryiso3
    """)

    result = await db.execute(raw_sql)
    rows = result.all()

    if not rows:
        return []

    # Step 2: min-max normalise each component across countries
    raw_vol = {r.countryiso3: float(r.volatility) for r in rows}
    raw_trend = {r.countryiso3: float(r.trend) for r in rows}
    raw_breadth = {r.countryiso3: float(r.breadth) for r in rows}

    norm_vol = _minmax_normalize(raw_vol)
    norm_trend = _minmax_normalize(raw_trend)
    norm_breadth = _minmax_normalize(raw_breadth)

    scores: list[CrisisScoreResponse] = []
    for r in rows:
        iso = r.countryiso3
        if country is not None and iso != country:
            continue
        v = norm_vol.get(iso, 0.0)
        t = norm_trend.get(iso, 0.0)
        b = norm_breadth.get(iso, 0.0)
        score = (0.40 * v + 0.35 * t + 0.25 * b) * 100
        scores.append(
            CrisisScoreResponse(
                countryiso3=iso,
                crisis_score=round(score, 2),
                severity=_severity(score),
                volatility_score=round(v * 100, 2),
                trend_score=round(t * 100, 2),
                breadth_score=round(b * 100, 2),
            )
        )

    scores.sort(key=lambda x: x.crisis_score, reverse=True)
    return scores
