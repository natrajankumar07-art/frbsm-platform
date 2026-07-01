"""
Evidence citation utilities for the Banking Intelligence layer.

Formats pre-computed engine outputs as citable evidence strings.
Every financial fact in an AI response must be traceable to one of these citations.

This module NEVER computes numbers — it only formats what the DB already contains.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Citation:
    metric: str
    value: str
    source: str
    formula_ref: str
    entity: str
    snapshot_date: str


def format_citation(c: Citation) -> str:
    return (
        f"{c.metric}: {c.value} "
        f"[Source: {c.source} | Ref: {c.formula_ref} | "
        f"Entity: {c.entity} | Snapshot: {c.snapshot_date}]"
    )


def _pct(raw: str | None) -> str:
    if raw is None:
        return "N/A"
    return f"{float(raw) * 100:.2f}%"


def _num(raw: str | None, currency: str = "INR") -> str:
    if raw is None:
        return "N/A"
    return f"{float(raw):,.2f} {currency}"


def build_lcr_citations(
    data: dict, entity: str, snapshot_date: str
) -> list[Citation]:
    """Build citations from an LCR analytics result dict."""
    cur = data.get("currency", "INR")
    return [
        Citation(
            metric="LCR Ratio",
            value=_pct(data.get("lcr_ratio")),
            source="BSM LCR Engine v1.0.0",
            formula_ref="BCBS LCR30.40 / LCR40.73",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="HQLA Total",
            value=_num(data.get("hqla_total"), cur),
            source="BSM LCR Engine v1.0.0",
            formula_ref="BCBS LCR30.40–LCR30.43",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Net Cash Outflows (NCO)",
            value=_num(data.get("net_cash_outflows"), cur),
            source="BSM LCR Engine v1.0.0",
            formula_ref="BCBS LCR40.73",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Total Outflows",
            value=_num(data.get("total_outflows"), cur),
            source="BSM LCR Engine v1.0.0",
            formula_ref="BCBS LCR40",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Total Inflows",
            value=_num(data.get("total_inflows"), cur),
            source="BSM LCR Engine v1.0.0",
            formula_ref="BCBS LCR40.73 (capped at 75% of outflows)",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
    ]


def build_nsfr_citations(
    data: dict, entity: str, snapshot_date: str
) -> list[Citation]:
    """Build citations from an NSFR analytics result dict."""
    cur = data.get("currency", "INR")
    return [
        Citation(
            metric="NSFR Ratio",
            value=_pct(data.get("nsfr_ratio")),
            source="BSM NSFR Engine v1.0.0",
            formula_ref="BCBS NSF20",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Available Stable Funding (ASF)",
            value=_num(data.get("available_stable_funding"), cur),
            source="BSM NSFR Engine v1.0.0",
            formula_ref="BCBS NSF30",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Required Stable Funding (RSF)",
            value=_num(data.get("required_stable_funding"), cur),
            source="BSM NSFR Engine v1.0.0",
            formula_ref="BCBS NSF40",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
    ]


def build_capital_citations(
    data: dict, entity: str, snapshot_date: str
) -> list[Citation]:
    """Build citations from a capital analytics result dict."""
    cur = data.get("currency", "INR")
    return [
        Citation(
            metric="CET1 Ratio",
            value=_pct(data.get("cet1_ratio")),
            source="BSM Capital Engine v1.0.0",
            formula_ref="BCBS CAP10 / RBI 2023-24 §3.1 (min 4.5%)",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Tier 1 Ratio",
            value=_pct(data.get("tier1_ratio")),
            source="BSM Capital Engine v1.0.0",
            formula_ref="BCBS CAP10 (min 6.0%)",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Total Capital Ratio (TCR)",
            value=_pct(data.get("total_capital_ratio")),
            source="BSM Capital Engine v1.0.0",
            formula_ref="BCBS CAP10 (min 8.0%)",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Leverage Ratio",
            value=_pct(data.get("leverage_ratio")),
            source="BSM Capital Engine v1.0.0",
            formula_ref="BCBS LEV10 (min 3.5%)",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Total RWA",
            value=_num(data.get("total_rwa"), cur),
            source="BSM Capital Engine v1.0.0",
            formula_ref="BCBS CRE20",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="CET1 Capital",
            value=_num(data.get("cet1_capital"), cur),
            source="BSM Capital Engine v1.0.0",
            formula_ref="BCBS CAP10",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
    ]


def build_balance_sheet_citations(
    data: dict, entity: str, snapshot_date: str
) -> list[Citation]:
    """Build citations from a balance sheet analytics result dict."""
    cur = data.get("currency", "INR")
    return [
        Citation(
            metric="Total Assets",
            value=_num(data.get("total_assets"), cur),
            source="BSM Balance Sheet Engine v1.0.0",
            formula_ref="IFRS Conceptual Framework / RBI Format A",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Total Liabilities",
            value=_num(data.get("total_liabilities"), cur),
            source="BSM Balance Sheet Engine v1.0.0",
            formula_ref="IFRS Conceptual Framework / RBI Format A",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Total Equity",
            value=_num(data.get("total_equity"), cur),
            source="BSM Balance Sheet Engine v1.0.0",
            formula_ref="IFRS Conceptual Framework / RBI Format A",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
        Citation(
            metric="Off-Balance Sheet Exposures",
            value=_num(data.get("off_balance_sheet"), cur),
            source="BSM Balance Sheet Engine v1.0.0",
            formula_ref="BCBS LEV10 (leverage exposure)",
            entity=entity,
            snapshot_date=snapshot_date,
        ),
    ]
