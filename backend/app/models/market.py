from sqlalchemy import CHAR, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    countryiso3: Mapped[str] = mapped_column(CHAR(3), nullable=False, index=True)
    admin1: Mapped[str | None] = mapped_column(String(200), nullable=True)
    admin2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    prices: Mapped[list["Price"]] = relationship("Price", back_populates="market")  # noqa: F821
