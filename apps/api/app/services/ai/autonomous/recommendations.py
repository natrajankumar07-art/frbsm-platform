"""
SAM Recommendation Engine (Epic 6).

Generates rule-based recommendations derived from engine outputs.
SAM NEVER computes ratios — all values come from the stored engine result tables.

Recommendation categories: liquidity, capital, funding, stress, regulatory
Priority: 1 (most urgent) → 5 (informational)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RecCategory(str, Enum):
    LIQUIDITY = "liquidity"
    CAPITAL = "capital"
    FUNDING = "funding"
    STRESS = "stress"
    REGULATORY = "regulatory"


@dataclass
class Recommendation:
    rec_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: str = ""
    priority: int = 3
    title: str = ""
    description: str = ""
    expected_benefit: str = ""
    potential_impact: str = ""
    evidence: dict = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "rec_id": self.rec_id,
            "category": self.category,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "expected_benefit": self.expected_benefit,
            "potential_impact": self.potential_impact,
            "evidence": self.evidence,
            "generated_at": self.generated_at,
        }


# ---------------------------------------------------------------------------
# Threshold constants (same as autonomous_monitor.py)
# ---------------------------------------------------------------------------

LCR_CRITICAL = 1.00
LCR_WARNING = 1.10
LCR_BUFFER = 1.20

NSFR_CRITICAL = 1.00
NSFR_WARNING = 1.05
NSFR_BUFFER = 1.10

CET1_CRITICAL = 0.045
CET1_WARNING = 0.060
CET1_BUFFER = 0.085

TCR_CRITICAL = 0.08
TCR_WARNING = 0.10

LEVERAGE_CRITICAL = 0.03
LEVERAGE_WARNING = 0.035


def generate_recommendations(
    entity_name: str,
    entity_id: str | None = None,
    lcr_ratio: float | None = None,
    nsfr_ratio: float | None = None,
    cet1_ratio: float | None = None,
    tier1_ratio: float | None = None,
    total_capital_ratio: float | None = None,
    leverage_ratio: float | None = None,
    open_alert_count: int = 0,
) -> list[Recommendation]:
    """
    Generate prioritised recommendations from engine output values.

    All ratio arguments should be in native form (e.g., 1.25 for 125% LCR).
    Capital ratios come as decimals from the engine (e.g., 0.0833 for 8.33%).
    """
    recs: list[Recommendation] = []

    # ── Liquidity actions ──────────────────────────────────────────────────
    if lcr_ratio is not None:
        if lcr_ratio < LCR_CRITICAL:
            recs.append(Recommendation(
                category=RecCategory.LIQUIDITY.value,
                priority=1,
                title="Restore LCR Compliance — Immediate Action Required",
                description=(
                    f"{entity_name} LCR ratio {lcr_ratio * 100:.1f}% is below the regulatory "
                    f"minimum of {LCR_CRITICAL * 100:.0f}%. Immediate liquidity action is required."
                ),
                expected_benefit="Return to regulatory compliance; prevent supervisory action.",
                potential_impact=(
                    "Failure to act risks regulatory intervention, increased supervisory scrutiny, "
                    "and potential restrictions on operations."
                ),
                evidence={
                    "lcr_ratio": lcr_ratio,
                    "minimum": LCR_CRITICAL,
                    "breach_pct": f"{(LCR_CRITICAL - lcr_ratio) * 100:.1f}pp",
                },
            ))
        elif lcr_ratio < LCR_WARNING:
            recs.append(Recommendation(
                category=RecCategory.LIQUIDITY.value,
                priority=2,
                title="Build HQLA Buffer to LCR Early Warning Level",
                description=(
                    f"{entity_name} LCR {lcr_ratio * 100:.1f}% is between the minimum "
                    f"({LCR_CRITICAL * 100:.0f}%) and early warning ({LCR_WARNING * 100:.0f}%) levels. "
                    "Increase Level 1 and Level 2A HQLA holdings."
                ),
                expected_benefit=f"Reach {LCR_WARNING * 100:.0f}% LCR early warning threshold.",
                potential_impact="Reducing HQLA below minimum triggers regulatory reporting.",
                evidence={"lcr_ratio": lcr_ratio, "target": LCR_WARNING},
            ))
        elif lcr_ratio < LCR_BUFFER:
            recs.append(Recommendation(
                category=RecCategory.LIQUIDITY.value,
                priority=4,
                title="Maintain LCR Liquidity Buffer Above 120%",
                description=(
                    f"{entity_name} LCR {lcr_ratio * 100:.1f}% meets minimum requirements but is "
                    f"below the {LCR_BUFFER * 100:.0f}% management buffer. "
                    "Consider optimising HQLA composition."
                ),
                expected_benefit="Improved liquidity resilience under stress scenarios.",
                potential_impact="Modest reduction in yield from holding lower-risk HQLA assets.",
                evidence={"lcr_ratio": lcr_ratio, "buffer_target": LCR_BUFFER},
            ))

    # ── Funding actions ────────────────────────────────────────────────────
    if nsfr_ratio is not None:
        if nsfr_ratio < NSFR_CRITICAL:
            recs.append(Recommendation(
                category=RecCategory.FUNDING.value,
                priority=1,
                title="Restore NSFR Compliance — Structural Funding Deficit",
                description=(
                    f"{entity_name} NSFR {nsfr_ratio * 100:.1f}% is below the "
                    f"{NSFR_CRITICAL * 100:.0f}% regulatory minimum. Review long-term funding mix."
                ),
                expected_benefit="Regulatory compliance; stable funding ratio restored.",
                potential_impact="Failure may require immediate balance sheet restructuring.",
                evidence={"nsfr_ratio": nsfr_ratio, "minimum": NSFR_CRITICAL},
            ))
        elif nsfr_ratio < NSFR_WARNING:
            recs.append(Recommendation(
                category=RecCategory.FUNDING.value,
                priority=2,
                title="Extend Funding Tenor to Strengthen NSFR",
                description=(
                    f"{entity_name} NSFR {nsfr_ratio * 100:.1f}% is approaching the minimum. "
                    "Issue longer-dated liabilities or term deposits to increase ASF."
                ),
                expected_benefit="Improved structural funding stability.",
                potential_impact="Marginal increase in funding cost from term premium.",
                evidence={"nsfr_ratio": nsfr_ratio, "target": NSFR_BUFFER},
            ))

    # ── Capital actions ────────────────────────────────────────────────────
    if cet1_ratio is not None:
        if cet1_ratio < CET1_CRITICAL:
            recs.append(Recommendation(
                category=RecCategory.CAPITAL.value,
                priority=1,
                title="Restore CET1 Compliance — Capital Breach",
                description=(
                    f"{entity_name} CET1 {cet1_ratio * 100:.2f}% is below the Basel III minimum "
                    f"of {CET1_CRITICAL * 100:.1f}%. Capital preservation and augmentation required."
                ),
                expected_benefit="Regulatory compliance; prevention of supervisory intervention.",
                potential_impact="Dividend restrictions and supervisory capital plan may be required.",
                evidence={"cet1_ratio": cet1_ratio, "minimum": CET1_CRITICAL},
            ))
        elif cet1_ratio < CET1_WARNING:
            recs.append(Recommendation(
                category=RecCategory.CAPITAL.value,
                priority=2,
                title="Rebuild CET1 Capital Buffer",
                description=(
                    f"{entity_name} CET1 {cet1_ratio * 100:.2f}% is between minimum ({CET1_CRITICAL * 100:.1f}%) "
                    f"and management buffer ({CET1_WARNING * 100:.1f}%). "
                    "Retain earnings and limit RWA growth."
                ),
                expected_benefit="Restore management buffer above regulatory minimums.",
                potential_impact="Potential constraint on dividend distributions.",
                evidence={"cet1_ratio": cet1_ratio, "target": CET1_WARNING},
            ))

    if total_capital_ratio is not None and total_capital_ratio < TCR_WARNING:
        recs.append(Recommendation(
            category=RecCategory.CAPITAL.value,
            priority=2,
            title="Strengthen Total Capital Ratio",
            description=(
                f"{entity_name} Total Capital Ratio {total_capital_ratio * 100:.2f}% is below "
                f"the {TCR_WARNING * 100:.0f}% management target. "
                "Review Tier 2 instrument issuance."
            ),
            expected_benefit="Improved capital buffer depth.",
            potential_impact="Potential additional funding cost from Tier 2 issuance.",
            evidence={"total_capital_ratio": total_capital_ratio, "target": TCR_WARNING},
        ))

    if leverage_ratio is not None and leverage_ratio < LEVERAGE_WARNING:
        recs.append(Recommendation(
            category=RecCategory.CAPITAL.value,
            priority=3,
            title="Monitor Leverage Ratio",
            description=(
                f"{entity_name} Leverage Ratio {leverage_ratio * 100:.2f}% is below "
                f"the {LEVERAGE_WARNING * 100:.1f}% management target. "
                "Review total exposure growth."
            ),
            expected_benefit="Reduced leverage ratio breach risk.",
            potential_impact="Constraining off-balance-sheet exposures reduces business flexibility.",
            evidence={"leverage_ratio": leverage_ratio, "target": LEVERAGE_WARNING},
        ))

    # ── Regulatory actions ─────────────────────────────────────────────────
    if open_alert_count >= 3:
        recs.append(Recommendation(
            category=RecCategory.REGULATORY.value,
            priority=2,
            title="Address Multiple Outstanding Regulatory Alerts",
            description=(
                f"{open_alert_count} active alerts require management attention. "
                "Prepare a remediation plan and brief the CRO within 24 hours."
            ),
            expected_benefit="Proactive regulatory posture; reduced supervisory risk.",
            potential_impact="Unaddressed alerts may trigger regulatory review.",
            evidence={"open_alert_count": open_alert_count},
        ))

    # ── Default informational recommendation ──────────────────────────────
    if not recs:
        recs.append(Recommendation(
            category=RecCategory.REGULATORY.value,
            priority=5,
            title="Continue Regular Monitoring Cadence",
            description=(
                f"{entity_name} regulatory metrics are within acceptable ranges. "
                "Maintain the current monitoring frequency and report generation schedule."
            ),
            expected_benefit="Early detection of emerging risks.",
            potential_impact="Minimal.",
            evidence={},
        ))

    recs.sort(key=lambda r: r.priority)
    return recs
