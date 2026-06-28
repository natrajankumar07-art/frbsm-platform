"""Scenario management ORM models — scenario definitions and parameter sets."""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

RATE = Numeric(precision=20, scale=8)


class ScenarioModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stress or sensitivity scenario definition."""

    __tablename__ = "scenarios"

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scenario_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_regulatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    regulatory_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(String(200), nullable=False)

    __table_args__ = (
        Index("ix_scenarios_type", "scenario_type"),
        Index("ix_scenarios_is_regulatory", "is_regulatory"),
        Index("ix_scenarios_is_active", "is_active"),
    )


class ScenarioParameterSetModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Parameter shocks attached to a scenario."""

    __tablename__ = "scenario_parameter_sets"

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    parameter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    shock_type: Mapped[str] = mapped_column(String(30), nullable=False)
    shock_value: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    asset_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    time_horizon_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_scenario_params_scenario_id", "scenario_id"),
        Index("ix_scenario_params_type", "parameter_type"),
    )
