from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.stress_test import (
    StressPositionImpactResponse,
    StressTestResultResponse,
    StressTestRunCreate,
    StressTestRunResponse,
    StressTestRunUpdate,
)
from ..services import stress_test as svc

router = APIRouter(prefix="/v1/stress-tests", tags=["Stress Tests"])


@router.get("", response_model=PagedResponse[StressTestRunResponse])
async def list_stress_runs(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("created_at"),
    sort_dir: SortDir = Query(SortDir.DESC),
    snapshot_id: uuid.UUID | None = Query(None),
    scenario_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    run_type: str | None = Query(None),
) -> PagedResponse[StressTestRunResponse]:
    return await svc.list_stress_runs(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        snapshot_id=snapshot_id,
        scenario_id=scenario_id,
        status=status,
        run_type=run_type,
    )


@router.post("", response_model=StressTestRunResponse, status_code=201)
async def create_stress_run(
    db: DBSession, payload: StressTestRunCreate
) -> StressTestRunResponse:
    return await svc.create_stress_run(db, payload)


@router.get("/{run_id}", response_model=StressTestRunResponse)
async def get_stress_run(db: DBSession, run_id: uuid.UUID) -> StressTestRunResponse:
    return await svc.get_stress_run(db, run_id)


@router.patch("/{run_id}", response_model=StressTestRunResponse)
async def update_stress_run(
    db: DBSession, run_id: uuid.UUID, payload: StressTestRunUpdate
) -> StressTestRunResponse:
    return await svc.update_stress_run(db, run_id, payload)


@router.delete("/{run_id}", status_code=204)
async def delete_stress_run(db: DBSession, run_id: uuid.UUID) -> None:
    await svc.delete_stress_run(db, run_id)


@router.get("/{run_id}/results", response_model=list[StressTestResultResponse])
async def list_stress_results(
    db: DBSession, run_id: uuid.UUID
) -> list[StressTestResultResponse]:
    return await svc.list_stress_results(db, run_id)


@router.get("/{run_id}/position-impacts", response_model=list[StressPositionImpactResponse])
async def list_position_impacts(
    db: DBSession, run_id: uuid.UUID
) -> list[StressPositionImpactResponse]:
    return await svc.list_position_impacts(db, run_id)
