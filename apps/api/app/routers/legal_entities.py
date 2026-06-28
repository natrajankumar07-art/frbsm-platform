from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.legal_entity import (
    CapitalRequirementCreate,
    CapitalRequirementResponse,
    LegalEntityCreate,
    LegalEntityResponse,
    LegalEntityUpdate,
)
from ..services import legal_entity as svc

router = APIRouter(prefix="/v1/legal-entities", tags=["Legal Entities"])


@router.get("", response_model=PagedResponse[LegalEntityResponse])
async def list_entities(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("created_at"),
    sort_dir: SortDir = Query(SortDir.DESC),
    q: str | None = Query(None),
    jurisdiction: str | None = Query(None),
    entity_type: str | None = Query(None),
    is_consolidated: bool | None = Query(None),
    is_reporting_entity: bool | None = Query(None),
) -> PagedResponse[LegalEntityResponse]:
    return await svc.list_entities(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        q=q,
        jurisdiction=jurisdiction,
        entity_type=entity_type,
        is_consolidated=is_consolidated,
        is_reporting_entity=is_reporting_entity,
    )


@router.post("", response_model=LegalEntityResponse, status_code=201)
async def create_entity(
    db: DBSession, payload: LegalEntityCreate
) -> LegalEntityResponse:
    return await svc.create_entity(db, payload)


@router.get("/{entity_id}", response_model=LegalEntityResponse)
async def get_entity(db: DBSession, entity_id: uuid.UUID) -> LegalEntityResponse:
    return await svc.get_entity(db, entity_id)


@router.patch("/{entity_id}", response_model=LegalEntityResponse)
async def update_entity(
    db: DBSession, entity_id: uuid.UUID, payload: LegalEntityUpdate
) -> LegalEntityResponse:
    return await svc.update_entity(db, entity_id, payload)


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(db: DBSession, entity_id: uuid.UUID) -> None:
    await svc.delete_entity(db, entity_id)


@router.get(
    "/{entity_id}/capital-requirements",
    response_model=list[CapitalRequirementResponse],
)
async def list_capital_requirements(
    db: DBSession, entity_id: uuid.UUID
) -> list[CapitalRequirementResponse]:
    return await svc.list_capital_requirements(db, entity_id)


@router.post(
    "/{entity_id}/capital-requirements",
    response_model=CapitalRequirementResponse,
    status_code=201,
)
async def add_capital_requirement(
    db: DBSession, entity_id: uuid.UUID, payload: CapitalRequirementCreate
) -> CapitalRequirementResponse:
    return await svc.add_capital_requirement(db, entity_id, payload)
