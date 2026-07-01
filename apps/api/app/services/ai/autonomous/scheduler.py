"""
Autonomous Background Scheduler (Epic 6).

Runs as an asyncio background task started in the FastAPI lifespan.

Schedule:
  Every 15 minutes: monitoring checks + alert/recommendation persistence
  Daily at 06:00 UTC: morning briefing generation
  Daily at 18:00 UTC: daily summary briefing
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)

MONITORING_INTERVAL_SECONDS = 900   # 15 minutes
SCHEDULER_RUNNING = False


async def _run_monitoring() -> None:
    """Run a single monitoring cycle using a fresh DB session."""
    try:
        from ....db.session import async_session_factory  # noqa: PLC0415
        from .monitor import run_persistent_monitoring  # noqa: PLC0415

        async with async_session_factory() as session:
            result = await run_persistent_monitoring(session)
            logger.info("scheduler_monitoring_complete", **result)
    except Exception as exc:
        logger.error("scheduler_monitoring_error", error=str(exc))


async def _run_morning_briefings() -> None:
    """Generate morning briefings for all active entities."""
    try:
        from ....db.models.autonomous import AutonomousAlertModel, AutonomousBriefingModel, AutonomousRecommendationModel  # noqa: PLC0415
        from ....db.models.legal_entity import LegalEntityModel  # noqa: PLC0415
        from ....db.session import async_session_factory  # noqa: PLC0415
        from sqlalchemy import select  # noqa: PLC0415
        from .briefing import BriefingInput, BriefingKeyMetrics, generate_briefing  # noqa: PLC0415
        from .monitor import _fetch_latest_metrics  # noqa: PLC0415

        async with async_session_factory() as session:
            entities = (await session.execute(
                select(LegalEntityModel).where(LegalEntityModel.is_reporting_entity == True).limit(10)  # noqa: E712
            )).scalars().all()

            if not entities:
                # Fallback: get first entity
                entities = (await session.execute(
                    select(LegalEntityModel).limit(1)
                )).scalars().all()

            for entity in entities:
                try:
                    metrics_dict = await _fetch_latest_metrics(session)
                    km = BriefingKeyMetrics(
                        lcr_ratio=metrics_dict.get("lcr_ratio"),
                        nsfr_ratio=metrics_dict.get("nsfr_ratio"),
                        cet1_ratio=metrics_dict.get("cet1_ratio"),
                        tier1_ratio=metrics_dict.get("tier1_ratio"),
                        total_capital_ratio=metrics_dict.get("total_capital_ratio"),
                        leverage_ratio=metrics_dict.get("leverage_ratio"),
                        snapshot_date=metrics_dict.get("snapshot_date"),
                    )

                    # Fetch open alerts and active recs
                    alerts = (await session.execute(
                        select(AutonomousAlertModel).where(
                            AutonomousAlertModel.status == "open"
                        ).order_by(AutonomousAlertModel.created_at.desc()).limit(5)
                    )).scalars().all()

                    recs = (await session.execute(
                        select(AutonomousRecommendationModel).where(
                            AutonomousRecommendationModel.status == "active"
                        ).order_by(AutonomousRecommendationModel.priority).limit(5)
                    )).scalars().all()

                    critical_count = sum(1 for a in alerts if a.severity == "critical")
                    warning_count = sum(1 for a in alerts if a.severity == "warning")

                    briefing_input = BriefingInput(
                        entity_name=entity.name,
                        briefing_type="morning",
                        metrics=km,
                        alert_count=len(alerts),
                        critical_alert_count=critical_count,
                        warning_alert_count=warning_count,
                        top_alerts=[{
                            "severity": a.severity,
                            "title": a.title,
                            "message": a.message[:100],
                        } for a in alerts],
                        top_recommendations=[{
                            "priority": r.priority,
                            "title": r.title,
                            "description": r.description[:100],
                            "category": r.category,
                        } for r in recs],
                    )

                    content = generate_briefing(briefing_input)
                    briefing = AutonomousBriefingModel(
                        id=uuid.uuid4(),
                        created_at=datetime.now(tz=timezone.utc),
                        entity_id=entity.id,
                        briefing_type="morning",
                        content=content,
                        key_metrics_json=json.dumps(km.to_dict()),
                        status="generated",
                    )
                    session.add(briefing)
                except Exception as exc:
                    logger.error("scheduler_briefing_entity_error", entity=entity.name, error=str(exc))

            await session.commit()
            logger.info("scheduler_morning_briefings_complete")
    except Exception as exc:
        logger.error("scheduler_morning_briefings_error", error=str(exc))


def _should_run_morning_briefing(now: datetime) -> bool:
    """True if current time is within the 06:00–07:00 UTC window."""
    return now.hour == 6 and now.minute < 15


async def run_scheduler() -> None:
    """
    Main scheduler loop. Runs indefinitely as a background asyncio task.
    Started from FastAPI lifespan.
    """
    global SCHEDULER_RUNNING
    SCHEDULER_RUNNING = True
    logger.info("autonomous_scheduler_started", interval_s=MONITORING_INTERVAL_SECONDS)

    last_briefing_date: str | None = None

    while True:
        try:
            now = datetime.now(tz=timezone.utc)

            # Always run monitoring
            await _run_monitoring()

            # Run morning briefing once per day in the 06:00 window
            today_str = now.strftime("%Y-%m-%d")
            if _should_run_morning_briefing(now) and last_briefing_date != today_str:
                await _run_morning_briefings()
                last_briefing_date = today_str

        except Exception as exc:
            logger.error("scheduler_cycle_error", error=str(exc))

        await asyncio.sleep(MONITORING_INTERVAL_SECONDS)


def get_scheduler_status() -> dict:
    return {
        "running": SCHEDULER_RUNNING,
        "interval_seconds": MONITORING_INTERVAL_SECONDS,
        "description": "Autonomous monitoring scheduler",
    }
