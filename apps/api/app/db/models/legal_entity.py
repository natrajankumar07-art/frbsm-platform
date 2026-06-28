"""Legal entity ORM models — the bank's own legal entities and capital requirements."""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

RATE = Numeric(precision=10, scale=6)


class LegalEntityModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "legal_entities"

    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    lei: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(10), nullable=False)
    regulator: Mapped[str] = mapped_column(String(50), nullable=False)
    license_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_consolidated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_reporting_entity: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    parent_entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    __table_args__ = (
        Index("ix_legal_entities_jurisdiction", "jurisdiction"),
        Index("ix_legal_entities_entity_type", "entity_type"),
        Index("ix_legal_entities_parent_entity_id", "parent_entity_id"),
    )


class EntityCapitalRequirementModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "entity_capital_requirements"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    requirement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    minimum_ratio: Mapped[float] = mapped_column(RATE, nullable=False)
    buffer_requirement: Mapped[float] = mapped_column(RATE, nullable=False, default=0.0)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    regulatory_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)

    __table_args__ = (
        Index("ix_ecr_entity_type", "entity_id", "requirement_type"),
        Index("ix_ecr_effective_from", "effective_from"),
    )
