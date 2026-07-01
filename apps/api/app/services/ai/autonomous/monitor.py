"""
Persistent autonomous monitor (Epic 6).

Wraps the stateless checks in autonomous_monitor.py and persists
new alerts + recommendations to the database.

Severity mapping from legacy 5-level → new 4-level:
  critical → critical
  high     → warning
  medium   → notice
  low      → notice
  info     → info
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.models.autonomous import (
    AutonomousAlertModel,
    AutonomousMonitoringRunModel,
    AutonomousRecommendationModel,
)
from ...ai.autonomous_monitor import run_monitoring_checks
from .recommendations import generate_recommendations
from .trend import detect_trend

logger = structlog.get_logger(__name__)

_SEVERITY_MAP = {
    "critical": "critical",
    "high": "warning",
    "medium": "notice",
    "low": "notice",
    "info": "info",
}


def _map_severity(old: str) -> str:
    return _SEVERITY_MAP.get(old.lower(), "info")


async def _fetch_latest_metrics(db: AsyncSession, entity_id: str | None = None) -> dict:
    """Fetch the most recent LCR, NSFR, Capital results from stored tables."""
    from ....db.models.capital import CapitalResultModel  # noqa: PLC0415
    from ....db.models.lcr import LCRResultModel  # noqa: PLC0415
    from ....db.models.nsfr import NSFRResultModel  # noqa: PLC0415
    from ....db.models.snapshot import SnapshotModel  # noqa: PLC0415

    metrics: dict = {}

    try:
        lcr_q = select(LCRResultModel, SnapshotModel.reporting_date).join(
            SnapshotModel, LCRResultModel.snapshot_id == SnapshotModel.id
        ).order_by(SnapshotModel.reporting_date.desc()).limit(1)
        row = (await db.execute(lcr_q)).first()
        if row:
            lcr, snap_date = row
            metrics["lcr_ratio"] = float(lcr.lcr_ratio) if lcr.lcr_ratio else None
            metrics["snapshot_date"] = str(snap_date)
    except Exception:
        pass

    try:
        nsfr_q = select(NSFRResultModel, SnapshotModel.reporting_date).join(
            SnapshotModel, NSFRResultModel.snapshot_id == SnapshotModel.id
        ).order_by(SnapshotModel.reporting_date.desc()).limit(1)
        row = (await db.execute(nsfr_q)).first()
        if row:
            nsfr, _ = row
            metrics["nsfr_ratio"] = float(nsfr.nsfr_ratio) if nsfr.nsfr_ratio else None
    except Exception:
        pass

    try:
        cap_q = select(CapitalResultModel, SnapshotModel.reporting_date).join(
            SnapshotModel, CapitalResultModel.snapshot_id == SnapshotModel.id
        ).order_by(SnapshotModel.reporting_date.desc()).limit(1)
        row = (await db.execute(cap_q)).first()
        if row:
            cap, _ = row
            metrics["cet1_ratio"] = float(cap.cet1_ratio) if cap.cet1_ratio else None
            metrics["tier1_ratio"] = float(cap.tier1_ratio) if cap.tier1_ratio else None
            metrics["total_capital_ratio"] = float(cap.total_capital_ratio) if cap.total_capital_ratio else None
            metrics["leverage_ratio"] = float(cap.leverage_ratio) if cap.leverage_ratio else None
            metrics["entity_id"] = str(cap.entity_id)
    except Exception:
        pass

    return metrics


async def _fetch_entity_name(db: AsyncSession, entity_id: str | None) -> str:
    if not entity_id:
        return "Unknown Entity"
    try:
        from ....db.models.legal_entity import LegalEntityModel  # noqa: PLC0415
        row = await db.get(LegalEntityModel, uuid.UUID(entity_id))
        return row.name if row else "Unknown Entity"
    except Exception:
        return "Unknown Entity"


async def run_persistent_monitoring(db: AsyncSession) -> dict:
    """
    Run monitoring checks and persist new alerts + recommendations.
    Returns a summary dict: alerts_generated, recommendations_generated, duration_ms.
    """
    t_start = time.time()
    alerts_generated = 0
    recs_generated = 0
    issues_created = 0

    try:
        # 1. Run legacy monitoring checks (stateless, in-memory)
        legacy_alerts = await run_monitoring_checks(db)

        # 2. Persist new alerts (deduplicate by title + category + current day)
        today = datetime.now(tz=timezone.utc).date()
        existing_titles = set()
        try:
            rows = await db.execute(
                select(AutonomousAlertModel.title).where(
                    AutonomousAlertModel.status == "open"
                ).limit(200)
            )
            existing_titles = {r[0] for r in rows}
        except Exception:
            pass

        for a in legacy_alerts:
            if a.title in existing_titles:
                continue
            new_alert = AutonomousAlertModel(
                id=uuid.uuid4(),
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
                category=a.category,
                severity=_map_severity(a.severity),
                title=a.title,
                message=a.message,
                metric_name=a.metric_name or None,
                metric_value=a.metric_value,
                threshold_value=a.threshold,
                snapshot_date=None,
                recommendation=None,
                evidence_json=json.dumps({
                    "metric_name": a.metric_name,
                    "metric_value": a.metric_value,
                    "threshold": a.threshold,
                    "entity": a.entity,
                    "snapshot_date": a.snapshot_date,
                }),
                status="open",
            )
            db.add(new_alert)
            alerts_generated += 1

        # 3. Fetch latest metrics for recommendation generation
        metrics = await _fetch_latest_metrics(db)
        entity_id = metrics.get("entity_id")
        entity_name = await _fetch_entity_name(db, entity_id)

        # 4. Generate and persist recommendations (replace active set daily)
        try:
            existing_recs = await db.execute(
                select(AutonomousRecommendationModel).where(
                    AutonomousRecommendationModel.status == "active"
                )
            )
            existing_recs_list = existing_recs.scalars().all()
            existing_rec_titles = {r.title for r in existing_recs_list}
        except Exception:
            existing_rec_titles = set()

        recs = generate_recommendations(
            entity_name=entity_name,
            entity_id=entity_id,
            lcr_ratio=metrics.get("lcr_ratio"),
            nsfr_ratio=metrics.get("nsfr_ratio"),
            cet1_ratio=metrics.get("cet1_ratio"),
            tier1_ratio=metrics.get("tier1_ratio"),
            total_capital_ratio=metrics.get("total_capital_ratio"),
            leverage_ratio=metrics.get("leverage_ratio"),
            open_alert_count=len(legacy_alerts),
        )

        for rec in recs:
            if rec.title in existing_rec_titles:
                continue
            new_rec = AutonomousRecommendationModel(
                id=uuid.uuid4(),
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc),
                category=rec.category,
                priority=rec.priority,
                title=rec.title,
                description=rec.description,
                expected_benefit=rec.expected_benefit,
                potential_impact=rec.potential_impact,
                evidence_json=json.dumps(rec.evidence),
                status="active",
            )
            db.add(new_rec)
            recs_generated += 1

        # 5. Log monitoring run
        duration_ms = int((time.time() - t_start) * 1000)
        run_record = AutonomousMonitoringRunModel(
            id=uuid.uuid4(),
            created_at=datetime.now(tz=timezone.utc),
            alerts_generated=alerts_generated,
            recommendations_generated=recs_generated,
            issues_created=issues_created,
            duration_ms=duration_ms,
            status="completed",
        )
        db.add(run_record)
        await db.commit()

        logger.info(
            "autonomous_monitor_run",
            alerts=alerts_generated,
            recommendations=recs_generated,
            duration_ms=duration_ms,
        )

        return {
            "alerts_generated": alerts_generated,
            "recommendations_generated": recs_generated,
            "issues_created": issues_created,
            "duration_ms": duration_ms,
            "status": "completed",
        }

    except Exception as exc:
        await db.rollback()
        duration_ms = int((time.time() - t_start) * 1000)
        logger.error("autonomous_monitor_error", error=str(exc))
        try:
            run_record = AutonomousMonitoringRunModel(
                id=uuid.uuid4(),
                created_at=datetime.now(tz=timezone.utc),
                alerts_generated=alerts_generated,
                recommendations_generated=0,
                issues_created=0,
                duration_ms=duration_ms,
                status="failed",
                error_message=str(exc)[:500],
            )
            db.add(run_record)
            await db.commit()
        except Exception:
            pass
        return {"alerts_generated": 0, "recommendations_generated": 0, "duration_ms": duration_ms, "status": "failed"}
