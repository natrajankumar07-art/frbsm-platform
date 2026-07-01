"""
Trend detection for autonomous monitoring (Epic 6).

Analyses a time-ordered sequence of metric values and classifies
the direction of change as:
  - improving      ≥ +5% change
  - stable         < ±5% change
  - deteriorating  ≤ −5% change
  - rapid_change   ≥ ±20% absolute change (regardless of direction)

No DB calls — operates on plain Python lists of floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TrendDirection(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DETERIORATING = "deteriorating"
    RAPID_CHANGE = "rapid_change"


@dataclass
class TrendResult:
    direction: str
    pct_change: float
    explanation: str
    previous_value: float | None = None
    latest_value: float | None = None


RAPID_THRESHOLD = 20.0   # ±20% is rapid
CHANGE_THRESHOLD = 5.0   # ±5% is meaningful


def detect_trend(values: list[float]) -> TrendResult:
    """
    Detect trend from a time-ordered sequence of metric values.

    Args:
        values: time-ordered list, oldest first, latest last.

    Returns:
        TrendResult with direction, pct_change, and explanation.
    """
    if len(values) < 2:
        return TrendResult(
            direction=TrendDirection.STABLE.value,
            pct_change=0.0,
            explanation="Insufficient data for trend analysis.",
            previous_value=values[0] if values else None,
            latest_value=values[0] if values else None,
        )

    latest = values[-1]
    previous = values[-2]

    if previous == 0.0:
        return TrendResult(
            direction=TrendDirection.STABLE.value,
            pct_change=0.0,
            explanation="Prior period value is zero; trend undefined.",
            previous_value=previous,
            latest_value=latest,
        )

    pct_change = (latest - previous) / abs(previous) * 100.0

    if abs(pct_change) >= RAPID_THRESHOLD:
        direction = TrendDirection.RAPID_CHANGE.value
        verb = "increased" if pct_change > 0 else "decreased"
        explanation = (
            f"Rapid movement: {verb} by {abs(pct_change):.1f}% vs prior period. "
            "Requires immediate management attention."
        )
    elif pct_change >= CHANGE_THRESHOLD:
        direction = TrendDirection.IMPROVING.value
        explanation = (
            f"Improving: increased by {pct_change:.1f}% vs prior period."
        )
    elif pct_change <= -CHANGE_THRESHOLD:
        direction = TrendDirection.DETERIORATING.value
        explanation = (
            f"Deteriorating: decreased by {abs(pct_change):.1f}% vs prior period."
        )
    else:
        direction = TrendDirection.STABLE.value
        explanation = (
            f"Stable: changed by {pct_change:+.1f}% vs prior period — within normal variation."
        )

    return TrendResult(
        direction=direction,
        pct_change=pct_change,
        explanation=explanation,
        previous_value=previous,
        latest_value=latest,
    )


def classify_metric_trend(metric_name: str, trend: TrendResult) -> str:
    """
    Generate a natural-language sentence describing the trend for a named metric.
    """
    pct_str = f"{abs(trend.pct_change):.1f}%"
    if trend.direction == TrendDirection.RAPID_CHANGE.value:
        verb = "surged" if trend.pct_change > 0 else "plunged"
        return f"{metric_name} {verb} by {pct_str} — rapid change warrants review."
    elif trend.direction == TrendDirection.IMPROVING.value:
        return f"{metric_name} improved by {pct_str} over the prior period."
    elif trend.direction == TrendDirection.DETERIORATING.value:
        return f"{metric_name} deteriorated by {pct_str} over the prior period."
    else:
        return f"{metric_name} is stable, with {pct_str} variation."
