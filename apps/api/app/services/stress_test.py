from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.stress_test import (
    stress_impact_repo,
    stress_result_repo,
    stress_run_repo,
)
from ..schemas.common import PagedResponse, SortDir
from ..schemas.stress_test import (
    StressPositionImpactResponse,
    StressTestResultResponse,
    StressTestRunCreate,
    StressTestRunResponse,
    StressTestRunUpdate,
)

_ALLOWED_SORT_BY = {"status", "run_type", "created_at", "updated_at"}


async def list_stress_runs(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    snapshot_id: uuid.UUID | None,
    scenario_id: uuid.UUID | None,
    status: str | None,
    run_type: str | None,
) -> PagedResponse[StressTestRunResponse]:
    if sort_by not in _ALLOWED_SORT_BY:
        sort_by = "created_at"
    items, total = await stress_run_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        snapshot_id=snapshot_id,
        scenario_id=scenario_id,
        status=status,
        run_type=run_type,
    )
    return PagedResponse.create(
        [StressTestRunResponse.model_validate(i) for i in items], total, page, size
    )


async def get_stress_run(
    db: AsyncSession, run_id: uuid.UUID
) -> StressTestRunResponse:
    run = await stress_run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Stress test run not found")
    return StressTestRunResponse.model_validate(run)


async def create_stress_run(
    db: AsyncSession, payload: StressTestRunCreate
) -> StressTestRunResponse:
    try:
        run = await stress_run_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Stress test run conflicts with existing data"
        )
    return StressTestRunResponse.model_validate(run)


async def update_stress_run(
    db: AsyncSession, run_id: uuid.UUID, payload: StressTestRunUpdate
) -> StressTestRunResponse:
    run = await stress_run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Stress test run not found")
    updated = await stress_run_repo.update_instance(
        db, run, **payload.model_dump(exclude_unset=True)
    )
    return StressTestRunResponse.model_validate(updated)


async def delete_stress_run(db: AsyncSession, run_id: uuid.UUID) -> None:
    run = await stress_run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Stress test run not found")
    try:
        await stress_run_repo.delete_instance(db, run)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Stress test run has results and cannot be deleted",
        )


async def list_stress_results(
    db: AsyncSession, run_id: uuid.UUID
) -> list[StressTestResultResponse]:
    run = await stress_run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Stress test run not found")
    items = await stress_result_repo.list_for_run(db, run_id)
    return [StressTestResultResponse.model_validate(i) for i in items]


async def list_position_impacts(
    db: AsyncSession, run_id: uuid.UUID
) -> list[StressPositionImpactResponse]:
    run = await stress_run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Stress test run not found")
    items = await stress_impact_repo.list_for_run(db, run_id)
    return [StressPositionImpactResponse.model_validate(i) for i in items]
