"""
Read-only analytics endpoints — surface pre-computed regulatory results.

These endpoints read stored result rows (lcr_results, nsfr_results,
capital_results, balance_sheet_summaries) populated during seeding / compute runs.
They do NOT recompute anything — engines are invoked separately.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from ..db.models.balance_sheet import BalanceSheetSummaryModel
from ..db.models.capital import CapitalResultModel
from ..db.models.lcr import LCRResultModel
from ..db.models.nsfr import NSFRResultModel
from ..db.models.position import PositionModel
from ..dependencies import DBSession

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class LCRSummary(BaseModel):
    snapshot_id: uuid.UUID
    entity_id: uuid.UUID
    hqla_total: Decimal
    net_cash_outflows: Decimal
    total_outflows: Decimal
    total_inflows: Decimal
    inflow_cap_applied: bool
    lcr_ratio: Decimal
    minimum_ratio: Decimal
    passes: bool
    currency: str


class NSFRSummary(BaseModel):
    snapshot_id: uuid.UUID
    entity_id: uuid.UUID
    available_stable_funding: Decimal
    required_stable_funding: Decimal
    nsfr_ratio: Decimal
    minimum_ratio: Decimal
    passes: bool
    currency: str


class CapitalSummary(BaseModel):
    snapshot_id: uuid.UUID
    entity_id: uuid.UUID
    cet1_capital: Decimal
    additional_tier1: Decimal
    tier2_capital: Decimal
    total_capital: Decimal
    rwa_credit: Decimal
    rwa_market: Decimal
    rwa_operational: Decimal
    total_rwa: Decimal
    cet1_ratio: Decimal
    tier1_ratio: Decimal
    total_capital_ratio: Decimal
    leverage_ratio: Decimal
    passes_all: bool
    currency: str


class BalanceSheetSummary(BaseModel):
    snapshot_id: uuid.UUID
    entity_id: uuid.UUID
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    off_balance_sheet: Decimal
    currency: str
    balances: bool


class PositionSummary(BaseModel):
    total_positions: int
    total_booked_amount: Decimal
    by_asset_class: dict[str, Decimal]
    by_hqla_level: dict[str, Decimal]
    by_deposit_type: dict[str, Decimal]
    currency: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/lcr", response_model=LCRSummary | None)
async def get_lcr_result(
    db: DBSession,
    snapshot_id: uuid.UUID,
    entity_id: uuid.UUID,
):
    row = await db.scalar(
        select(LCRResultModel).where(
            LCRResultModel.snapshot_id == snapshot_id,
            LCRResultModel.entity_id == entity_id,
        )
    )
    if not row:
        return None
    return LCRSummary(
        snapshot_id=row.snapshot_id,
        entity_id=row.entity_id,
        hqla_total=row.hqla_total,
        net_cash_outflows=row.net_cash_outflows,
        total_outflows=row.total_outflows,
        total_inflows=row.total_inflows,
        inflow_cap_applied=row.inflow_cap_applied,
        lcr_ratio=row.lcr_ratio,
        minimum_ratio=row.minimum_ratio,
        passes=row.passes,
        currency=row.currency,
    )


@router.get("/nsfr", response_model=NSFRSummary | None)
async def get_nsfr_result(
    db: DBSession,
    snapshot_id: uuid.UUID,
    entity_id: uuid.UUID,
):
    row = await db.scalar(
        select(NSFRResultModel).where(
            NSFRResultModel.snapshot_id == snapshot_id,
            NSFRResultModel.entity_id == entity_id,
        )
    )
    if not row:
        return None
    return NSFRSummary(
        snapshot_id=row.snapshot_id,
        entity_id=row.entity_id,
        available_stable_funding=row.available_stable_funding,
        required_stable_funding=row.required_stable_funding,
        nsfr_ratio=row.nsfr_ratio,
        minimum_ratio=row.minimum_ratio,
        passes=row.passes,
        currency=row.currency,
    )


@router.get("/capital", response_model=CapitalSummary | None)
async def get_capital_result(
    db: DBSession,
    snapshot_id: uuid.UUID,
    entity_id: uuid.UUID,
):
    row = await db.scalar(
        select(CapitalResultModel).where(
            CapitalResultModel.snapshot_id == snapshot_id,
            CapitalResultModel.entity_id == entity_id,
        )
    )
    if not row:
        return None
    return CapitalSummary(
        snapshot_id=row.snapshot_id,
        entity_id=row.entity_id,
        cet1_capital=row.cet1_capital,
        additional_tier1=row.additional_tier1,
        tier2_capital=row.tier2_capital,
        total_capital=row.total_capital,
        rwa_credit=row.rwa_credit,
        rwa_market=row.rwa_market,
        rwa_operational=row.rwa_operational,
        total_rwa=row.total_rwa,
        cet1_ratio=row.cet1_ratio,
        tier1_ratio=row.tier1_ratio,
        total_capital_ratio=row.total_capital_ratio,
        leverage_ratio=row.leverage_ratio,
        passes_all=row.passes_all,
        currency=row.currency,
    )


@router.get("/balance-sheet", response_model=BalanceSheetSummary | None)
async def get_balance_sheet_result(
    db: DBSession,
    snapshot_id: uuid.UUID,
    entity_id: uuid.UUID,
):
    row = await db.scalar(
        select(BalanceSheetSummaryModel).where(
            BalanceSheetSummaryModel.snapshot_id == snapshot_id,
            BalanceSheetSummaryModel.entity_id == entity_id,
        )
    )
    if not row:
        return None
    # Compute balance check: assets == liabilities + equity within 1 unit
    balances = abs(row.total_assets - (row.total_liabilities + row.total_equity)) <= Decimal("1")
    return BalanceSheetSummary(
        snapshot_id=row.snapshot_id,
        entity_id=row.entity_id,
        total_assets=row.total_assets,
        total_liabilities=row.total_liabilities,
        total_equity=row.total_equity,
        off_balance_sheet=row.total_off_balance_sheet,
        currency=row.currency,
        balances=balances,
    )


@router.get("/positions/summary", response_model=PositionSummary)
async def get_position_summary(
    db: DBSession,
    entity_id: uuid.UUID,
    snapshot_id: uuid.UUID | None = None,
):
    rows = (
        await db.scalars(
            select(PositionModel).where(PositionModel.status == "active")
        )
    ).all()

    by_asset_class: dict[str, Decimal] = {}
    by_hqla_level: dict[str, Decimal] = {}
    by_deposit_type: dict[str, Decimal] = {}
    total = Decimal("0")

    for p in rows:
        amt = p.booked_amount or Decimal("0")
        total += amt
        by_asset_class[p.asset_class] = by_asset_class.get(p.asset_class, Decimal("0")) + amt
        by_hqla_level[p.hqla_level] = by_hqla_level.get(p.hqla_level, Decimal("0")) + amt
        if p.deposit_type:
            by_deposit_type[p.deposit_type] = (
                by_deposit_type.get(p.deposit_type, Decimal("0")) + amt
            )

    return PositionSummary(
        total_positions=len(rows),
        total_booked_amount=total,
        by_asset_class=by_asset_class,
        by_hqla_level=by_hqla_level,
        by_deposit_type=by_deposit_type,
        currency="INR",
    )
