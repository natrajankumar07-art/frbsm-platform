from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.scenario import scenario_param_repo, scenario_repo
from ..schemas.common import PagedResponse, SortDir
from ..schemas.scenario import (
    ScenarioCreate,
    ScenarioParameterCreate,
    ScenarioParameterResponse,
    ScenarioResponse,
    ScenarioUpdate,
)

_ALLOWED_SORT_BY = {
    "name", "code", "scenario_type", "severity", "created_at", "updated_at"
}


async def list_scenarios(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    q: str | None,
    scenario_type: str | None,
    severity: str | None,
    is_regulatory: bool | None,
    is_active: bool | None,
) -> PagedResponse[ScenarioResponse]:
    if sort_by not in _ALLOWED_SORT_BY:
        sort_by = "created_at"
    items, total = await scenario_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        q=q,
        scenario_type=scenario_type,
        severity=severity,
        is_regulatory=is_regulatory,
        is_active=is_active,
    )
    return PagedResponse.create(
        [ScenarioResponse.model_validate(i) for i in items], total, page, size
    )


async def get_scenario(db: AsyncSession, scenario_id: uuid.UUID) -> ScenarioResponse:
    scenario = await scenario_repo.get_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return ScenarioResponse.model_validate(scenario)


async def create_scenario(
    db: AsyncSession, payload: ScenarioCreate
) -> ScenarioResponse:
    try:
        scenario = await scenario_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Scenario code already exists")
    return ScenarioResponse.model_validate(scenario)


async def update_scenario(
    db: AsyncSession, scenario_id: uuid.UUID, payload: ScenarioUpdate
) -> ScenarioResponse:
    scenario = await scenario_repo.get_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    updated = await scenario_repo.update_instance(
        db, scenario, **payload.model_dump(exclude_unset=True)
    )
    return ScenarioResponse.model_validate(updated)


async def delete_scenario(db: AsyncSession, scenario_id: uuid.UUID) -> None:
    scenario = await scenario_repo.get_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    try:
        await scenario_repo.delete_instance(db, scenario)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Scenario has associated runs and cannot be deleted",
        )


async def list_scenario_parameters(
    db: AsyncSession, scenario_id: uuid.UUID
) -> list[ScenarioParameterResponse]:
    scenario = await scenario_repo.get_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    items = await scenario_param_repo.list_for_scenario(db, scenario_id)
    return [ScenarioParameterResponse.model_validate(i) for i in items]


async def add_scenario_parameter(
    db: AsyncSession, scenario_id: uuid.UUID, payload: ScenarioParameterCreate
) -> ScenarioParameterResponse:
    scenario = await scenario_repo.get_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    item = await scenario_param_repo.create(
        db, scenario_id=scenario_id, **payload.model_dump()
    )
    return ScenarioParameterResponse.model_validate(item)
