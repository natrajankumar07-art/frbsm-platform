"""
Scenario Engine — applies scenario parameter shocks to engine inputs.

This layer sits between the raw position data and the compute engines.
It modifies LCR/NSFR/Capital inputs according to scenario parameters before
the engines are re-run to produce stressed results.

Shock types:
    absolute : result = baseline + shock_value
    relative : result = baseline × (1 + shock_value)
    replace  : result = shock_value
"""

from __future__ import annotations

from decimal import Decimal

from engines.common.models import (
    CapitalInput,
    LCRInput,
    NSFRInput,
    OutflowItem,
    RWAPositionItem,
    ScenarioParameter,
)

VERSION = "1.0.0"


def _apply_shock(baseline: Decimal, shock_type: str, shock_value: Decimal) -> Decimal:
    if shock_type == "absolute":
        return baseline + shock_value
    if shock_type == "relative":
        return baseline * (Decimal("1") + shock_value)
    if shock_type == "replace":
        return shock_value
    raise ValueError(f"Unknown shock_type: {shock_type!r}")


def apply_lcr_shocks(
    lcr_input: LCRInput,
    parameters: list[ScenarioParameter],
) -> LCRInput:
    """
    Apply liquidity scenario shocks to an LCR input, returning a new LCRInput.

    Supported parameter names:
      liquidity.outflow_shock  — scales all run-off rates (relative shock)
      liquidity.hqla_shock     — scales all HQLA gross amounts (relative shock)
    """
    outflow_items = list(lcr_input.outflow_items)
    hqla_positions = list(lcr_input.hqla_positions)

    for param in parameters:
        if param.parameter_type != "liquidity":
            continue
        if param.parameter_name == "outflow_shock":
            # Scale all run-off rates (cap at 100%)
            outflow_items = [
                item.model_copy(update={
                    "run_off_rate": min(
                        _apply_shock(item.run_off_rate, param.shock_type, param.shock_value),
                        Decimal("1"),
                    )
                })
                for item in outflow_items
            ]
        elif param.parameter_name == "hqla_shock":
            # Scale all HQLA gross amounts (floor at 0)
            hqla_positions = [
                pos.model_copy(update={
                    "gross_amount": max(
                        _apply_shock(pos.gross_amount, param.shock_type, param.shock_value),
                        Decimal("0"),
                    )
                })
                for pos in hqla_positions
            ]

    return lcr_input.model_copy(update={
        "outflow_items": outflow_items,
        "hqla_positions": hqla_positions,
    })


def apply_nsfr_shocks(
    nsfr_input: NSFRInput,
    parameters: list[ScenarioParameter],
) -> NSFRInput:
    """
    Apply shocks to an NSFR input.

    Supported parameter names:
      liquidity.asf_shock  — scales all ASF factors
      liquidity.rsf_shock  — scales all RSF factors
    """
    funding_items = list(nsfr_input.funding_items)
    asset_items = list(nsfr_input.asset_items)

    for param in parameters:
        if param.parameter_type != "liquidity":
            continue
        if param.parameter_name == "asf_shock":
            funding_items = [
                item.model_copy(update={
                    "asf_factor": max(
                        min(_apply_shock(item.asf_factor, param.shock_type, param.shock_value), Decimal("1")),
                        Decimal("0"),
                    )
                })
                for item in funding_items
            ]
        elif param.parameter_name == "rsf_shock":
            asset_items = [
                item.model_copy(update={
                    "rsf_factor": max(
                        min(_apply_shock(item.rsf_factor, param.shock_type, param.shock_value), Decimal("1")),
                        Decimal("0"),
                    )
                })
                for item in asset_items
            ]

    return nsfr_input.model_copy(update={
        "funding_items": funding_items,
        "asset_items": asset_items,
    })


def apply_capital_shocks(
    capital_input: CapitalInput,
    parameters: list[ScenarioParameter],
) -> CapitalInput:
    """
    Apply shocks to a Capital input.

    Supported parameter names:
      capital.rwa_shock    — scales all credit RWA position risk weights
      credit.rwa_shock     — same as capital.rwa_shock
    """
    rwa_positions = list(capital_input.rwa_positions)
    rwa_market = capital_input.rwa_market
    rwa_operational = capital_input.rwa_operational

    for param in parameters:
        if param.parameter_name == "rwa_shock" and param.parameter_type in ("capital", "credit"):
            rwa_positions = [
                pos.model_copy(update={
                    "risk_weight": max(
                        _apply_shock(pos.risk_weight, param.shock_type, param.shock_value),
                        Decimal("0"),
                    )
                })
                for pos in rwa_positions
            ]
            rwa_market = max(_apply_shock(rwa_market, param.shock_type, param.shock_value), Decimal("0"))
            rwa_operational = max(_apply_shock(rwa_operational, param.shock_type, param.shock_value), Decimal("0"))

    return capital_input.model_copy(update={
        "rwa_positions": rwa_positions,
        "rwa_market": rwa_market,
        "rwa_operational": rwa_operational,
    })
