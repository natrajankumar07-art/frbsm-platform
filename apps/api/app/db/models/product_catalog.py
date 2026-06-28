"""Product catalog ORM models — product groups, products, behavioral assumptions."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

RATE = Numeric(precision=10, scale=6)


class ProductGroupModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_groups"

    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_group_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_product_groups_parent", "parent_group_id"),
        Index("ix_product_groups_code", "code", unique=True),
    )


class ProductModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_group_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    asset_class: Mapped[str] = mapped_column(String(50), nullable=False)
    instrument_type: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    basel_asset_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lcr_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    nsfr_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ifrs9_scope: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("ix_products_product_group_id", "product_group_id"),
        Index("ix_products_asset_class", "asset_class"),
        Index("ix_products_instrument_type", "instrument_type"),
        Index("ix_products_code", "code", unique=True),
    )


class ProductBehavioralAssumptionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_behavioral_assumptions"

    product_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    assumption_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    parameter_value: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    regulatory_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)

    __table_args__ = (
        Index("ix_pba_product_id", "product_id"),
        Index("ix_pba_assumption_type", "assumption_type"),
        Index("ix_pba_effective_from", "effective_from"),
    )
