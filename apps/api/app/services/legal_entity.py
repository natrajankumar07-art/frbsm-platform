from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.legal_entity import capital_req_repo, legal_entity_repo
from ..schemas.common import PagedResponse, SortDir
from ..schemas.legal_entity import (
    CapitalRequirementCreate,
    CapitalRequirementResponse,
    LegalEntityCreate,
    LegalEntityResponse,
    LegalEntityUpdate,
)

_ALLOWED_SORT_BY = {
    "name", "code", "lei", "entity_type", "jurisdiction", "created_at", "updated_at"
}


async def list_entities(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    q: str | None,
    jurisdiction: str | None,
    entity_type: str | None,
    is_consolidated: bool | None,
    is_reporting_entity: bool | None,
) -> PagedResponse[LegalEntityResponse]:
    if sort_by not in _ALLOWED_SORT_BY:
        sort_by = "created_at"
    items, total = await legal_entity_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        q=q,
        jurisdiction=jurisdiction,
        entity_type=entity_type,
        is_consolidated=is_consolidated,
        is_reporting_entity=is_reporting_entity,
    )
    return PagedResponse.create(
        [LegalEntityResponse.model_validate(i) for i in items], total, page, size
    )


async def get_entity(db: AsyncSession, entity_id: uuid.UUID) -> LegalEntityResponse:
    entity = await legal_entity_repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Legal entity not found")
    return LegalEntityResponse.model_validate(entity)


async def create_entity(
    db: AsyncSession, payload: LegalEntityCreate
) -> LegalEntityResponse:
    try:
        entity = await legal_entity_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Legal entity code already exists")
    return LegalEntityResponse.model_validate(entity)


async def update_entity(
    db: AsyncSession, entity_id: uuid.UUID, payload: LegalEntityUpdate
) -> LegalEntityResponse:
    entity = await legal_entity_repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Legal entity not found")
    try:
        updated = await legal_entity_repo.update_instance(
            db, entity, **payload.model_dump(exclude_unset=True)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Update conflicts with existing data")
    return LegalEntityResponse.model_validate(updated)


async def delete_entity(db: AsyncSession, entity_id: uuid.UUID) -> None:
    entity = await legal_entity_repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Legal entity not found")
    try:
        await legal_entity_repo.delete_instance(db, entity)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Entity has dependents and cannot be deleted"
        )


async def list_capital_requirements(
    db: AsyncSession, entity_id: uuid.UUID
) -> list[CapitalRequirementResponse]:
    entity = await legal_entity_repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Legal entity not found")
    items = await capital_req_repo.list_for_entity(db, entity_id)
    return [CapitalRequirementResponse.model_validate(i) for i in items]


async def add_capital_requirement(
    db: AsyncSession, entity_id: uuid.UUID, payload: CapitalRequirementCreate
) -> CapitalRequirementResponse:
    entity = await legal_entity_repo.get_by_id(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Legal entity not found")
    item = await capital_req_repo.create(db, entity_id=entity_id, **payload.model_dump())
    return CapitalRequirementResponse.model_validate(item)
