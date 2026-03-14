from datetime import date, datetime

from sqlalchemy import CHAR, NUMERIC, DATE, TIMESTAMP, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Price(Base):
    __tablename__ = "prices"

    __table_args__ = (
        Index("ix_prices_countryiso3_date", "countryiso3", "date"),
        Index("ix_prices_commodity_id_date", "commodity_id", "date"),
        Index("ix_prices_market_id", "market_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(DATE, nullable=False)
    countryiso3: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    admin1: Mapped[str | None] = mapped_column(String(200), nullable=True)
    admin2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    market_id: Mapped[int] = mapped_column(Integer, ForeignKey("markets.id"), nullable=False)
    commodity_id: Mapped[int] = mapped_column(Integer, ForeignKey("commodities.id"), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priceflag: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pricetype: Mapped[str | None] = mapped_column(String(20), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), ForeignKey("currencies.code"), nullable=False)
    price: Mapped[float | None] = mapped_column(NUMERIC(12, 4), nullable=True)
    usdprice: Mapped[float | None] = mapped_column(NUMERIC(12, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    market: Mapped["Market"] = relationship("Market", back_populates="prices")  # noqa: F821
    commodity: Mapped["Commodity"] = relationship("Commodity", back_populates="prices")  # noqa: F821
    currency: Mapped["Currency"] = relationship("Currency", back_populates="prices")  # noqa: F821
