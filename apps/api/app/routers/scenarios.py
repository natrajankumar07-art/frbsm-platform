from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.scenario import (
    ScenarioCreate,
    ScenarioParameterCreate,
    ScenarioParameterResponse,
    ScenarioResponse,
    ScenarioUpdate,
)
from ..services import scenario as svc

router = APIRouter(prefix="/v1/scenarios", tags=["Scenarios"])


@router.get("", response_model=PagedResponse[ScenarioResponse])
async def list_scenarios(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("created_at"),
    sort_dir: SortDir = Query(SortDir.DESC),
    q: str | None = Query(None),
    scenario_type: str | None = Query(None),
    severity: str | None = Query(None),
    is_regulatory: bool | None = Query(None),
    is_active: bool | None = Query(None),
) -> PagedResponse[ScenarioResponse]:
    return await svc.list_scenarios(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        q=q,
        scenario_type=scenario_type,
        severity=severity,
        is_regulatory=is_regulatory,
        is_active=is_active,
    )


@router.post("", response_model=ScenarioResponse, status_code=201)
async def create_scenario(db: DBSession, payload: ScenarioCreate) -> ScenarioResponse:
    return await svc.create_scenario(db, payload)


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(db: DBSession, scenario_id: uuid.UUID) -> ScenarioResponse:
    return await svc.get_scenario(db, scenario_id)


@router.patch("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    db: DBSession, scenario_id: uuid.UUID, payload: ScenarioUpdate
) -> ScenarioResponse:
    return await svc.update_scenario(db, scenario_id, payload)


@router.delete("/{scenario_id}", status_code=204)
async def delete_scenario(db: DBSession, scenario_id: uuid.UUID) -> None:
    await svc.delete_scenario(db, scenario_id)


@router.get(
    "/{scenario_id}/parameters", response_model=list[ScenarioParameterResponse]
)
async def list_scenario_parameters(
    db: DBSession, scenario_id: uuid.UUID
) -> list[ScenarioParameterResponse]:
    return await svc.list_scenario_parameters(db, scenario_id)


@router.post(
    "/{scenario_id}/parameters",
    response_model=ScenarioParameterResponse,
    status_code=201,
)
async def add_scenario_parameter(
    db: DBSession, scenario_id: uuid.UUID, payload: ScenarioParameterCreate
) -> ScenarioParameterResponse:
    return await svc.add_scenario_parameter(db, scenario_id, payload)
