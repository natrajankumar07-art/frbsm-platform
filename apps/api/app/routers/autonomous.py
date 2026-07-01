"""
Epic 6 — Autonomous Banking Intelligence endpoints.

  GET  /v1/autonomous/alerts                    — list persisted alerts
  PATCH /v1/autonomous/alerts/{id}/status       — update alert status
  GET  /v1/autonomous/recommendations           — list recommendations
  PATCH /v1/autonomous/recommendations/{id}/status — update recommendation status
  GET  /v1/autonomous/issues                    — list outstanding issues
  POST /v1/autonomous/issues                    — create issue
  PATCH /v1/autonomous/issues/{id}/status       — update issue status
  GET  /v1/autonomous/briefings                 — list briefings
  POST /v1/autonomous/briefings/generate        — generate briefing on demand
  GET  /v1/autonomous/scheduled-reports         — list schedules
  POST /v1/autonomous/scheduled-reports         — create schedule
  PATCH /v1/autonomous/scheduled-reports/{id}  — update schedule
  DELETE /v1/autonomous/scheduled-reports/{id} — delete schedule
  GET  /v1/autonomous/activity                  — activity feed
  POST /v1/autonomous/monitor/run               — trigger manual monitoring run
  GET  /v1/autonomous/status                    — scheduler status
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..dependencies import DBSession
from ..db.models.autonomous import (
    AutonomousAlertModel,
    AutonomousBriefingModel,
    AutonomousIssueModel,
    AutonomousMonitoringRunModel,
    AutonomousRecommendationModel,
    ScheduledReportConfigModel,
)
from ..schemas.autonomous import (
    ActivityItem,
    ActivityResponse,
    AlertResponse,
    AlertsResponse,
    AlertStatusUpdate,
    BriefingGenerateRequest,
    BriefingResponse,
    BriefingsResponse,
    IssueCreateRequest,
    IssueResponse,
    IssuesResponse,
    IssueStatusUpdate,
    MonitoringRunResponse,
    RecommendationResponse,
    RecommendationsResponse,
    RecommendationStatusUpdate,
    ScheduledReportCreateRequest,
    ScheduledReportResponse,
    ScheduledReportsResponse,
    ScheduledReportUpdateRequest,
    SchedulerStatusResponse,
)
from ..services.ai.autonomous.briefing import (
    BriefingInput,
    BriefingKeyMetrics,
    generate_briefing,
)
from ..services.ai.autonomous.issues import (
    create_issue,
    list_issues,
    update_issue_status,
)
from ..services.ai.autonomous.monitor import (
    _fetch_latest_metrics,
    run_persistent_monitoring,
)
from ..services.ai.autonomous.scheduler import get_scheduler_status

router = APIRouter(prefix="/v1/autonomous", tags=["Autonomous Intelligence"])
logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _alert_to_response(a: AutonomousAlertModel) -> AlertResponse:
    evidence: dict = {}
    try:
        evidence = json.loads(a.evidence_json or "{}")
    except Exception:
        pass
    return AlertResponse(
        id=str(a.id),
        created_at=a.created_at,
        entity_id=str(a.entity_id) if a.entity_id else None,
        category=a.category,
        severity=a.severity,
        title=a.title,
        message=a.message,
        metric_name=a.metric_name,
        metric_value=a.metric_value,
        threshold_value=a.threshold_value,
        snapshot_date=str(a.snapshot_date) if a.snapshot_date else None,
        recommendation=a.recommendation,
        evidence=evidence,
        status=a.status,
        acknowledged_at=a.acknowledged_at,
        resolved_at=a.resolved_at,
    )


def _rec_to_response(r: AutonomousRecommendationModel) -> RecommendationResponse:
    evidence: dict = {}
    try:
        evidence = json.loads(r.evidence_json or "{}")
    except Exception:
        pass
    return RecommendationResponse(
        id=str(r.id),
        created_at=r.created_at,
        entity_id=str(r.entity_id) if r.entity_id else None,
        category=r.category,
        priority=r.priority,
        title=r.title,
        description=r.description,
        expected_benefit=r.expected_benefit,
        potential_impact=r.potential_impact,
        evidence=evidence,
        status=r.status,
        implemented_at=r.implemented_at,
        dismissed_at=r.dismissed_at,
    )


def _issue_to_response(i: AutonomousIssueModel) -> IssueResponse:
    ctx: dict = {}
    try:
        ctx = json.loads(i.context_json or "{}")
    except Exception:
        pass
    return IssueResponse(
        id=str(i.id),
        created_at=i.created_at,
        updated_at=i.updated_at,
        entity_id=str(i.entity_id) if i.entity_id else None,
        title=i.title,
        description=i.description,
        category=i.category,
        severity=i.severity,
        status=i.status,
        resolved_at=i.resolved_at,
        context=ctx,
    )


def _briefing_to_response(b: AutonomousBriefingModel) -> BriefingResponse:
    km: dict = {}
    try:
        km = json.loads(b.key_metrics_json or "{}")
    except Exception:
        pass
    return BriefingResponse(
        id=str(b.id),
        created_at=b.created_at,
        entity_id=str(b.entity_id) if b.entity_id else None,
        briefing_type=b.briefing_type,
        content=b.content,
        key_metrics=km,
        status=b.status,
        delivered_at=b.delivered_at,
    )


def _schedule_to_response(s: ScheduledReportConfigModel) -> ScheduledReportResponse:
    return ScheduledReportResponse(
        id=str(s.id),
        created_at=s.created_at,
        updated_at=s.updated_at,
        entity_id=str(s.entity_id) if s.entity_id else None,
        report_type=s.report_type,
        schedule_type=s.schedule_type,
        enabled=s.enabled,
        last_run=s.last_run,
        next_run=s.next_run,
        created_by=s.created_by,
    )


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    db: DBSession,
    status: str | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> AlertsResponse:
    q = select(AutonomousAlertModel).order_by(AutonomousAlertModel.created_at.desc())
    if status:
        q = q.where(AutonomousAlertModel.status == status)
    if severity:
        q = q.where(AutonomousAlertModel.severity == severity)
    rows = (await db.execute(q.limit(limit))).scalars().all()

    alerts = [_alert_to_response(a) for a in rows]
    return AlertsResponse(
        alerts=alerts,
        total=len(alerts),
        critical_count=sum(1 for a in alerts if a.severity == "critical"),
        warning_count=sum(1 for a in alerts if a.severity == "warning"),
        notice_count=sum(1 for a in alerts if a.severity == "notice"),
        info_count=sum(1 for a in alerts if a.severity == "info"),
    )


@router.patch("/alerts/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: str,
    body: AlertStatusUpdate,
    db: DBSession,
) -> AlertResponse:
    alert = await db.get(AutonomousAlertModel, uuid.UUID(alert_id))
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = body.status
    alert.updated_at = datetime.now(tz=timezone.utc)
    if body.status == "acknowledged":
        alert.acknowledged_at = datetime.now(tz=timezone.utc)
    elif body.status == "resolved":
        alert.resolved_at = datetime.now(tz=timezone.utc)
    await db.flush()
    return _alert_to_response(alert)


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    db: DBSession,
    status: str | None = "active",
    limit: int = 20,
) -> RecommendationsResponse:
    q = select(AutonomousRecommendationModel).order_by(
        AutonomousRecommendationModel.priority,
        AutonomousRecommendationModel.created_at.desc(),
    )
    if status:
        q = q.where(AutonomousRecommendationModel.status == status)
    rows = (await db.execute(q.limit(limit))).scalars().all()
    recs = [_rec_to_response(r) for r in rows]
    return RecommendationsResponse(recommendations=recs, total=len(recs))


@router.patch("/recommendations/{rec_id}/status", response_model=RecommendationResponse)
async def update_recommendation_status(
    rec_id: str,
    body: RecommendationStatusUpdate,
    db: DBSession,
) -> RecommendationResponse:
    rec = await db.get(AutonomousRecommendationModel, uuid.UUID(rec_id))
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = body.status
    rec.updated_at = datetime.now(tz=timezone.utc)
    if body.status == "implemented":
        rec.implemented_at = datetime.now(tz=timezone.utc)
    elif body.status == "dismissed":
        rec.dismissed_at = datetime.now(tz=timezone.utc)
    await db.flush()
    return _rec_to_response(rec)


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

@router.get("/issues", response_model=IssuesResponse)
async def get_issues(
    db: DBSession,
    status: str | None = None,
    entity_id: str | None = None,
    limit: int = 50,
) -> IssuesResponse:
    issues = await list_issues(db, status=status, entity_id=entity_id, limit=limit)
    items = [_issue_to_response(i) for i in issues]
    return IssuesResponse(
        issues=items,
        total=len(items),
        open_count=sum(1 for i in items if i.status == "open"),
        monitoring_count=sum(1 for i in items if i.status == "monitoring"),
        resolved_count=sum(1 for i in items if i.status == "resolved"),
    )


@router.post("/issues", response_model=IssueResponse, status_code=201)
async def create_new_issue(body: IssueCreateRequest, db: DBSession) -> IssueResponse:
    issue = await create_issue(
        db,
        title=body.title,
        description=body.description,
        category=body.category,
        severity=body.severity,
        entity_id=body.entity_id,
        context=body.context,
    )
    await db.flush()
    return _issue_to_response(issue)


@router.patch("/issues/{issue_id}/status", response_model=IssueResponse)
async def update_issue(
    issue_id: str,
    body: IssueStatusUpdate,
    db: DBSession,
) -> IssueResponse:
    issue = await update_issue_status(db, issue_id=issue_id, status=body.status)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    await db.flush()
    return _issue_to_response(issue)


# ---------------------------------------------------------------------------
# Briefings
# ---------------------------------------------------------------------------

@router.get("/briefings", response_model=BriefingsResponse)
async def get_briefings(
    db: DBSession,
    briefing_type: str | None = None,
    limit: int = 20,
) -> BriefingsResponse:
    q = select(AutonomousBriefingModel).order_by(AutonomousBriefingModel.created_at.desc())
    if briefing_type:
        q = q.where(AutonomousBriefingModel.briefing_type == briefing_type)
    rows = (await db.execute(q.limit(limit))).scalars().all()
    items = [_briefing_to_response(b) for b in rows]
    return BriefingsResponse(briefings=items, total=len(items))


@router.post("/briefings/generate", response_model=BriefingResponse, status_code=201)
async def generate_briefing_on_demand(
    body: BriefingGenerateRequest,
    db: DBSession,
) -> BriefingResponse:
    """Generate an executive briefing on demand using latest engine outputs."""
    metrics_dict = await _fetch_latest_metrics(db)

    entity_name = "Unknown Entity"
    entity_id_val = None
    if body.entity_id:
        entity_id_val = uuid.UUID(body.entity_id)
        from ..db.models.legal_entity import LegalEntityModel  # noqa: PLC0415
        ent = await db.get(LegalEntityModel, entity_id_val)
        if ent:
            entity_name = ent.name
    elif metrics_dict.get("entity_id"):
        entity_id_val_str = metrics_dict["entity_id"]
        try:
            entity_id_val = uuid.UUID(entity_id_val_str)
            from ..db.models.legal_entity import LegalEntityModel  # noqa: PLC0415
            ent = await db.get(LegalEntityModel, entity_id_val)
            if ent:
                entity_name = ent.name
        except Exception:
            pass

    # Fetch alerts and recommendations for context
    alerts = (await db.execute(
        select(AutonomousAlertModel).where(
            AutonomousAlertModel.status == "open"
        ).order_by(AutonomousAlertModel.created_at.desc()).limit(5)
    )).scalars().all()

    recs = (await db.execute(
        select(AutonomousRecommendationModel).where(
            AutonomousRecommendationModel.status == "active"
        ).order_by(AutonomousRecommendationModel.priority).limit(5)
    )).scalars().all()

    km = BriefingKeyMetrics(
        lcr_ratio=metrics_dict.get("lcr_ratio"),
        nsfr_ratio=metrics_dict.get("nsfr_ratio"),
        cet1_ratio=metrics_dict.get("cet1_ratio"),
        tier1_ratio=metrics_dict.get("tier1_ratio"),
        total_capital_ratio=metrics_dict.get("total_capital_ratio"),
        leverage_ratio=metrics_dict.get("leverage_ratio"),
        snapshot_date=metrics_dict.get("snapshot_date"),
    )

    critical_count = sum(1 for a in alerts if a.severity == "critical")
    warning_count = sum(1 for a in alerts if a.severity == "warning")
    issues = await list_issues(db, status="open", limit=100)

    briefing_input = BriefingInput(
        entity_name=entity_name,
        briefing_type=body.briefing_type,
        metrics=km,
        alert_count=len(alerts),
        critical_alert_count=critical_count,
        warning_alert_count=warning_count,
        open_issue_count=len(issues),
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
        entity_id=entity_id_val,
        briefing_type=body.briefing_type,
        content=content,
        key_metrics_json=json.dumps(km.to_dict()),
        status="generated",
    )
    db.add(briefing)
    await db.flush()
    return _briefing_to_response(briefing)


# ---------------------------------------------------------------------------
# Scheduled Reports
# ---------------------------------------------------------------------------

@router.get("/scheduled-reports", response_model=ScheduledReportsResponse)
async def get_scheduled_reports(db: DBSession) -> ScheduledReportsResponse:
    rows = (await db.execute(
        select(ScheduledReportConfigModel).order_by(ScheduledReportConfigModel.created_at.desc())
    )).scalars().all()
    items = [_schedule_to_response(s) for s in rows]
    return ScheduledReportsResponse(configs=items, total=len(items))


@router.post("/scheduled-reports", response_model=ScheduledReportResponse, status_code=201)
async def create_scheduled_report(
    body: ScheduledReportCreateRequest,
    db: DBSession,
) -> ScheduledReportResponse:
    from ..services.ai.autonomous.scheduler import _compute_next_run  # type: ignore[attr-defined]  # noqa: PLC0415
    config = ScheduledReportConfigModel(
        id=uuid.uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
        entity_id=uuid.UUID(body.entity_id) if body.entity_id else None,
        report_type=body.report_type,
        schedule_type=body.schedule_type,
        enabled=body.enabled,
        created_by="user",
    )
    db.add(config)
    await db.flush()
    return _schedule_to_response(config)


@router.patch("/scheduled-reports/{config_id}", response_model=ScheduledReportResponse)
async def update_scheduled_report(
    config_id: str,
    body: ScheduledReportUpdateRequest,
    db: DBSession,
) -> ScheduledReportResponse:
    config = await db.get(ScheduledReportConfigModel, uuid.UUID(config_id))
    if not config:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if body.enabled is not None:
        config.enabled = body.enabled
    if body.schedule_type is not None:
        config.schedule_type = body.schedule_type
    config.updated_at = datetime.now(tz=timezone.utc)
    await db.flush()
    return _schedule_to_response(config)


@router.delete("/scheduled-reports/{config_id}", status_code=204)
async def delete_scheduled_report(config_id: str, db: DBSession) -> None:
    config = await db.get(ScheduledReportConfigModel, uuid.UUID(config_id))
    if not config:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await db.delete(config)
    await db.flush()


# ---------------------------------------------------------------------------
# Activity Feed
# ---------------------------------------------------------------------------

@router.get("/activity", response_model=ActivityResponse)
async def get_activity(db: DBSession, limit: int = 30) -> ActivityResponse:
    """Return a chronological feed of autonomous actions (alerts + briefings + runs)."""
    items: list[ActivityItem] = []

    try:
        alerts = (await db.execute(
            select(AutonomousAlertModel).order_by(
                AutonomousAlertModel.created_at.desc()
            ).limit(10)
        )).scalars().all()
        for a in alerts:
            items.append(ActivityItem(
                id=str(a.id),
                type="alert_raised",
                title=f"Alert: {a.title}",
                detail=a.message[:120],
                severity=a.severity,
                timestamp=a.created_at,
            ))
    except Exception:
        pass

    try:
        briefings = (await db.execute(
            select(AutonomousBriefingModel).order_by(
                AutonomousBriefingModel.created_at.desc()
            ).limit(5)
        )).scalars().all()
        for b in briefings:
            items.append(ActivityItem(
                id=str(b.id),
                type="briefing_generated",
                title=f"Briefing: {b.briefing_type.replace('_', ' ').title()}",
                detail=f"SAM generated a {b.briefing_type} executive briefing.",
                severity=None,
                timestamp=b.created_at,
            ))
    except Exception:
        pass

    try:
        runs = (await db.execute(
            select(AutonomousMonitoringRunModel).order_by(
                AutonomousMonitoringRunModel.created_at.desc()
            ).limit(10)
        )).scalars().all()
        for r in runs:
            items.append(ActivityItem(
                id=str(r.id),
                type="monitoring_run",
                title="Monitoring Cycle Completed",
                detail=(
                    f"{r.alerts_generated} alert(s), {r.recommendations_generated} recommendation(s) generated. "
                    f"Duration: {r.duration_ms or 0}ms."
                ),
                severity=None,
                timestamp=r.created_at,
            ))
    except Exception:
        pass

    items.sort(key=lambda x: x.timestamp, reverse=True)
    items = items[:limit]
    return ActivityResponse(items=items, total=len(items))


# ---------------------------------------------------------------------------
# Monitoring trigger + status
# ---------------------------------------------------------------------------

@router.post("/monitor/run", response_model=MonitoringRunResponse)
async def trigger_monitoring_run(db: DBSession) -> MonitoringRunResponse:
    """Trigger a manual monitoring cycle."""
    result = await run_persistent_monitoring(db)
    run_record = (await db.execute(
        select(AutonomousMonitoringRunModel).order_by(
            AutonomousMonitoringRunModel.created_at.desc()
        ).limit(1)
    )).scalars().first()
    if not run_record:
        raise HTTPException(status_code=500, detail="Monitoring run failed")
    return MonitoringRunResponse(
        id=str(run_record.id),
        created_at=run_record.created_at,
        alerts_generated=run_record.alerts_generated,
        recommendations_generated=run_record.recommendations_generated,
        issues_created=run_record.issues_created,
        duration_ms=run_record.duration_ms,
        status=run_record.status,
        error_message=run_record.error_message,
    )


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_status(db: DBSession) -> SchedulerStatusResponse:
    status = get_scheduler_status()
    last_run_row = (await db.execute(
        select(AutonomousMonitoringRunModel).order_by(
            AutonomousMonitoringRunModel.created_at.desc()
        ).limit(1)
    )).scalars().first()
    return SchedulerStatusResponse(
        running=status["running"],
        interval_seconds=status["interval_seconds"],
        description=status["description"],
        last_run=last_run_row.created_at if last_run_row else None,
    )
