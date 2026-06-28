"""
Balance Sheet Engine.

Classifies positions into assets and liabilities and produces a structured
balance sheet summary with breakdown by asset class and funding type.

Asset classification:
    Positions where deposit_type is None are assets (loans, bonds, CRR etc.)
    Positions where deposit_type is not None are liabilities (deposits, borrowed funds)

Equity = total_equity input (if provided) or derived as assets − liabilities.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from engines.common.audit import EngineResult, build_trace
from engines.common.models import BalanceSheetInput
from engines.common.utils import canonical_hash, quantize

VERSION = "1.0.0"

_FORMULA_REFS = [
    "IFRS Conceptual Framework — Assets, liabilities, and equity definitions",
    "RBI Format A — Balance Sheet of a Scheduled Commercial Bank",
]

_BALANCE_TOLERANCE = Decimal("1")  # INR 1 crore tolerance for float noise


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class BalanceSheetResult(BaseModel):
    """Aggregated balance sheet with asset/liability/equity breakdown."""
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    asset_breakdown: dict[str, Decimal]      # asset_class → booked amount
    liability_breakdown: dict[str, Decimal]  # deposit_type → booked amount
    off_balance_sheet: Decimal
    currency: str
    balances: bool  # assets == liabilities + equity within tolerance


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_balance_sheet(inputs: BalanceSheetInput) -> EngineResult[BalanceSheetResult]:
    """
    Aggregate positions into a balance sheet summary.

    An asset/liability distinction is made by deposit_type:
    - deposit_type is None  → asset (loan, bond, security, CRR)
    - deposit_type not None → liability (deposit, borrowing, secured funding)

    Negative booked_amount values are accepted for short positions.
    """
    inputs_hash = canonical_hash(inputs.model_dump(mode="json"))

    asset_breakdown: dict[str, Decimal] = {}
    liability_breakdown: dict[str, Decimal] = {}

    for pos in inputs.positions:
        if pos.deposit_type is None:
            # Asset
            key = pos.asset_class
            asset_breakdown[key] = asset_breakdown.get(key, Decimal("0")) + pos.booked_amount
        else:
            # Liability
            key = pos.deposit_type
            liability_breakdown[key] = liability_breakdown.get(key, Decimal("0")) + abs(pos.booked_amount)

    total_assets = quantize(sum(asset_breakdown.values(), Decimal("0")))
    total_liabilities = quantize(sum(liability_breakdown.values(), Decimal("0")))

    if inputs.total_equity is not None:
        equity = inputs.total_equity
    else:
        equity = quantize(total_assets - total_liabilities)

    balances = abs(total_assets - (total_liabilities + equity)) <= _BALANCE_TOLERANCE

    result = BalanceSheetResult(
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_equity=quantize(equity),
        asset_breakdown={k: quantize(v) for k, v in asset_breakdown.items()},
        liability_breakdown={k: quantize(v) for k, v in liability_breakdown.items()},
        off_balance_sheet=inputs.off_balance_sheet_items,
        currency=inputs.currency,
        balances=balances,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="balance_sheet",
        version=VERSION,
        function="compute_balance_sheet",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)
