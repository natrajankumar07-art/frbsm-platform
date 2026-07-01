"""
Financial context builder for the AI Copilot.

Reads pre-computed regulatory results from the database and formats them
as structured text for injection into the AI system prompt.

This module NEVER computes any financial numbers. It only reads and formats
results that were previously computed by the deterministic Python engines.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.balance_sheet import BalanceSheetSummaryModel
from ...db.models.capital import CapitalResultModel
from ...db.models.lcr import LCRResultModel
from ...db.models.legal_entity import LegalEntityModel
from ...db.models.nsfr import NSFRResultModel
from ...db.models.snapshot import SnapshotModel


async def build_financial_context(
    db: AsyncSession,
    entity_id: uuid.UUID | None,
    snapshot_id: uuid.UUID | None,
) -> str:
    """
    Build a structured financial context string from stored engine results.

    Returns an empty string when entity_id or snapshot_id is not provided,
    so the AI still works as a general regulatory assistant without data.
    """
    if entity_id is None or snapshot_id is None:
        return ""

    # Load entity and snapshot metadata
    entity = await db.scalar(
        select(LegalEntityModel).where(LegalEntityModel.id == entity_id)
    )
    snapshot = await db.scalar(
        select(SnapshotModel).where(SnapshotModel.id == snapshot_id)
    )
    if not entity or not snapshot:
        return ""

    lines: list[str] = [
        "[COMPUTED BY BSM ENGINES — DO NOT RECALCULATE]",
        f"Entity: {entity.name} | Snapshot: {snapshot.reporting_date} ({snapshot.status})",
        "",
    ]

    # LCR
    lcr = await db.scalar(
        select(LCRResultModel).where(
            LCRResultModel.snapshot_id == snapshot_id,
            LCRResultModel.entity_id == entity_id,
        )
    )
    if lcr:
        lcr_pct = float(lcr.lcr_ratio) * 100
        min_pct = float(lcr.minimum_ratio) * 100
        status = "✓ PASS" if lcr.passes else "✗ FAIL"
        lines += [
            "LIQUIDITY COVERAGE RATIO (Basel III LCR30/40)",
            f"  HQLA Total:            {float(lcr.hqla_total):>14,.2f} {lcr.currency}",
            f"  Total Outflows:        {float(lcr.total_outflows):>14,.2f} {lcr.currency}",
            f"  Total Inflows:         {float(lcr.total_inflows):>14,.2f} {lcr.currency}",
            f"  Net Cash Outflows:     {float(lcr.net_cash_outflows):>14,.2f} {lcr.currency}",
            f"  LCR Ratio:             {lcr_pct:>13.2f}%  {status} (minimum: {min_pct:.2f}%)",
            f"  Inflow Cap Applied:    {'Yes' if lcr.inflow_cap_applied else 'No'}",
            "",
        ]

    # NSFR
    nsfr = await db.scalar(
        select(NSFRResultModel).where(
            NSFRResultModel.snapshot_id == snapshot_id,
            NSFRResultModel.entity_id == entity_id,
        )
    )
    if nsfr:
        nsfr_pct = float(nsfr.nsfr_ratio) * 100
        min_pct = float(nsfr.minimum_ratio) * 100
        status = "✓ PASS" if nsfr.passes else "✗ FAIL"
        surplus = float(nsfr.available_stable_funding) - float(nsfr.required_stable_funding)
        lines += [
            "NET STABLE FUNDING RATIO (Basel III NSF20)",
            f"  Available Stable Funding (ASF): {float(nsfr.available_stable_funding):>10,.2f} {nsfr.currency}",
            f"  Required Stable Funding  (RSF): {float(nsfr.required_stable_funding):>10,.2f} {nsfr.currency}",
            f"  ASF Surplus:                    {surplus:>10,.2f} {nsfr.currency}",
            f"  NSFR Ratio:              {nsfr_pct:>13.2f}%  {status} (minimum: {min_pct:.2f}%)",
            "",
        ]

    # Capital
    cap = await db.scalar(
        select(CapitalResultModel).where(
            CapitalResultModel.snapshot_id == snapshot_id,
            CapitalResultModel.entity_id == entity_id,
        )
    )
    if cap:
        status = "✓ PASS" if cap.passes_all else "✗ FAIL"
        lines += [
            "CAPITAL ADEQUACY (Basel III CAP10 / RBI 2023-24)",
            f"  CET1 Capital:          {float(cap.cet1_capital):>14,.2f} {cap.currency}",
            f"  Additional Tier 1:     {float(cap.additional_tier1):>14,.2f} {cap.currency}",
            f"  Tier 2 Capital:        {float(cap.tier2_capital):>14,.2f} {cap.currency}",
            f"  Total Capital:         {float(cap.total_capital):>14,.2f} {cap.currency}",
            f"  Total RWA:             {float(cap.total_rwa):>14,.2f} {cap.currency}",
            f"    Credit RWA:          {float(cap.rwa_credit):>14,.2f}",
            f"    Market RWA:          {float(cap.rwa_market):>14,.2f}",
            f"    Operational RWA:     {float(cap.rwa_operational):>14,.2f}",
            f"  CET1 Ratio:            {float(cap.cet1_ratio)*100:>13.2f}%  (minimum: 4.50%)",
            f"  Tier 1 Ratio:          {float(cap.tier1_ratio)*100:>13.2f}%  (minimum: 6.00%)",
            f"  Total Capital Ratio:   {float(cap.total_capital_ratio)*100:>13.2f}%  (minimum: 8.00%)",
            f"  Leverage Ratio:        {float(cap.leverage_ratio)*100:>13.2f}%  (minimum: 3.50%)",
            f"  All Minimums:          {status}",
            "",
        ]

    # Balance Sheet
    bs = await db.scalar(
        select(BalanceSheetSummaryModel).where(
            BalanceSheetSummaryModel.snapshot_id == snapshot_id,
            BalanceSheetSummaryModel.entity_id == entity_id,
        )
    )
    if bs:
        lines += [
            "BALANCE SHEET SUMMARY (IFRS / RBI Format A)",
            f"  Total Assets:          {float(bs.total_assets):>14,.2f} {bs.currency}",
            f"  Total Liabilities:     {float(bs.total_liabilities):>14,.2f} {bs.currency}",
            f"  Total Equity:          {float(bs.total_equity):>14,.2f} {bs.currency}",
            f"  Off-Balance Sheet:     {float(bs.total_off_balance_sheet):>14,.2f} {bs.currency}",
            f"  Balance Sheet Balances: {'Yes' if abs(bs.total_assets - (bs.total_liabilities + bs.total_equity)) <= 1 else 'No'}",
            "",
        ]

    return "\n".join(lines)


async def get_financial_data(
    db: AsyncSession,
    entity_id: uuid.UUID | None,
    snapshot_id: uuid.UUID | None,
) -> dict:
    """
    Return raw engine result data as a plain dict for the reasoning layer.

    Keys: entity_name, snapshot_date, lcr, nsfr, capital, balance_sheet.
    Each value is a dict of raw field values (str-serialised Decimals) or None.
    This function NEVER computes; it only reads and converts stored rows.
    """
    if entity_id is None or snapshot_id is None:
        return {}

    entity = await db.scalar(
        select(LegalEntityModel).where(LegalEntityModel.id == entity_id)
    )
    snapshot = await db.scalar(
        select(SnapshotModel).where(SnapshotModel.id == snapshot_id)
    )
    if not entity or not snapshot:
        return {}

    result: dict = {
        "entity_name": entity.name,
        "snapshot_date": str(snapshot.reporting_date),
        "lcr": None,
        "nsfr": None,
        "capital": None,
        "balance_sheet": None,
    }

    lcr = await db.scalar(
        select(LCRResultModel).where(
            LCRResultModel.snapshot_id == snapshot_id,
            LCRResultModel.entity_id == entity_id,
        )
    )
    if lcr:
        result["lcr"] = {
            "lcr_ratio": str(lcr.lcr_ratio),
            "hqla_total": str(lcr.hqla_total),
            "total_outflows": str(lcr.total_outflows),
            "total_inflows": str(lcr.total_inflows),
            "net_cash_outflows": str(lcr.net_cash_outflows),
            "minimum_ratio": str(lcr.minimum_ratio),
            "passes": lcr.passes,
            "inflow_cap_applied": lcr.inflow_cap_applied,
            "currency": lcr.currency,
        }

    nsfr = await db.scalar(
        select(NSFRResultModel).where(
            NSFRResultModel.snapshot_id == snapshot_id,
            NSFRResultModel.entity_id == entity_id,
        )
    )
    if nsfr:
        result["nsfr"] = {
            "nsfr_ratio": str(nsfr.nsfr_ratio),
            "available_stable_funding": str(nsfr.available_stable_funding),
            "required_stable_funding": str(nsfr.required_stable_funding),
            "minimum_ratio": str(nsfr.minimum_ratio),
            "passes": nsfr.passes,
            "currency": nsfr.currency,
        }

    cap = await db.scalar(
        select(CapitalResultModel).where(
            CapitalResultModel.snapshot_id == snapshot_id,
            CapitalResultModel.entity_id == entity_id,
        )
    )
    if cap:
        result["capital"] = {
            "cet1_ratio": str(cap.cet1_ratio),
            "tier1_ratio": str(cap.tier1_ratio),
            "total_capital_ratio": str(cap.total_capital_ratio),
            "leverage_ratio": str(cap.leverage_ratio),
            "cet1_capital": str(cap.cet1_capital),
            "additional_tier1": str(cap.additional_tier1),
            "tier2_capital": str(cap.tier2_capital),
            "total_capital": str(cap.total_capital),
            "total_rwa": str(cap.total_rwa),
            "rwa_credit": str(cap.rwa_credit),
            "rwa_market": str(cap.rwa_market),
            "rwa_operational": str(cap.rwa_operational),
            "passes_all": cap.passes_all,
            "currency": cap.currency,
        }

    bs = await db.scalar(
        select(BalanceSheetSummaryModel).where(
            BalanceSheetSummaryModel.snapshot_id == snapshot_id,
            BalanceSheetSummaryModel.entity_id == entity_id,
        )
    )
    if bs:
        result["balance_sheet"] = {
            "total_assets": str(bs.total_assets),
            "total_liabilities": str(bs.total_liabilities),
            "total_equity": str(bs.total_equity),
            "off_balance_sheet": str(bs.total_off_balance_sheet),
            "currency": bs.currency,
        }

    return result
