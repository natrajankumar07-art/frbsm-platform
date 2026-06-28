from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.counterparty import counterparty_repo
from ..schemas.common import PagedResponse, SortDir
from ..schemas.counterparty import (
    CounterpartyCreate,
    CounterpartyResponse,
    CounterpartyUpdate,
)

_ALLOWED_SORT_BY = {
    "name", "sector", "geography", "jurisdiction", "rating", "created_at", "updated_at"
}


async def list_counterparties(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    q: str | None,
    sector: str | None,
    jurisdiction: str | None,
    rating: str | None,
    is_financial_institution: bool | None,
) -> PagedResponse[CounterpartyResponse]:
    if sort_by not in _ALLOWED_SORT_BY:
        sort_by = "created_at"
    items, total = await counterparty_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        q=q,
        sector=sector,
        jurisdiction=jurisdiction,
        rating=rating,
        is_financial_institution=is_financial_institution,
    )
    return PagedResponse.create(
        [CounterpartyResponse.model_validate(i) for i in items], total, page, size
    )


async def get_counterparty(
    db: AsyncSession, counterparty_id: uuid.UUID
) -> CounterpartyResponse:
    cp = await counterparty_repo.get_by_id(db, counterparty_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    return CounterpartyResponse.model_validate(cp)


async def create_counterparty(
    db: AsyncSession, payload: CounterpartyCreate
) -> CounterpartyResponse:
    try:
        cp = await counterparty_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Counterparty already exists")
    return CounterpartyResponse.model_validate(cp)


async def update_counterparty(
    db: AsyncSession, counterparty_id: uuid.UUID, payload: CounterpartyUpdate
) -> CounterpartyResponse:
    cp = await counterparty_repo.get_by_id(db, counterparty_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    try:
        updated = await counterparty_repo.update_instance(
            db, cp, **payload.model_dump(exclude_unset=True)
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Update conflicts with existing data")
    return CounterpartyResponse.model_validate(updated)


async def delete_counterparty(db: AsyncSession, counterparty_id: uuid.UUID) -> None:
    cp = await counterparty_repo.get_by_id(db, counterparty_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    try:
        await counterparty_repo.delete_instance(db, cp)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Counterparty has associated positions and cannot be deleted",
        )
