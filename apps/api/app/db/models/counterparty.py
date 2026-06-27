"""Counterparty ORM model."""

import uuid

from sqlalchemy import Boolean, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CounterpartyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "counterparties"

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    lei: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True, index=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    geography: Mapped[str] = mapped_column(String(2), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(10), nullable=False)
    group_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    group_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating: Mapped[str] = mapped_column(String(10), nullable=False, default="UNRATED")
    is_financial_institution: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_sovereign: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_large_exposure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    positions: Mapped[list["PositionModel"]] = relationship(  # type: ignore[name-defined]
        "PositionModel",
        back_populates="counterparty",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_counterparties_jurisdiction", "jurisdiction"),
        Index("ix_counterparties_sector", "sector"),
        Index("ix_counterparties_group_id", "group_id"),
    )
