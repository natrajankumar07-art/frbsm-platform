from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.position import collateral_repo, position_repo
from ..schemas.common import PagedResponse, SortDir
from ..schemas.position import (
    CollateralCreate,
    CollateralResponse,
    PositionCreate,
    PositionResponse,
    PositionUpdate,
)

_ALLOWED_SORT_BY = {
    "reporting_date", "asset_class", "currency", "notional",
    "fair_value", "status", "created_at", "updated_at"
}


async def list_positions(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    counterparty_id: uuid.UUID | None,
    reporting_date: date | None,
    asset_class: str | None,
    currency: str | None,
    status: str | None,
    hqla_level: str | None,
    ifrs9_stage: str | None,
) -> PagedResponse[PositionResponse]:
    if sort_by not in _ALLOWED_SORT_BY:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by '{sort_by}'. Allowed: {sorted(_ALLOWED_SORT_BY)}")
    items, total = await position_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        counterparty_id=counterparty_id,
        reporting_date=reporting_date,
        asset_class=asset_class,
        currency=currency,
        status=status,
        hqla_level=hqla_level,
        ifrs9_stage=ifrs9_stage,
    )
    return PagedResponse.create(
        [PositionResponse.model_validate(i) for i in items], total, page, size
    )


async def get_position(db: AsyncSession, position_id: uuid.UUID) -> PositionResponse:
    pos = await position_repo.get_by_id(db, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    return PositionResponse.model_validate(pos)


async def create_position(
    db: AsyncSession, payload: PositionCreate
) -> PositionResponse:
    try:
        pos = await position_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Position conflicts with existing data"
        )
    return PositionResponse.model_validate(pos)


async def update_position(
    db: AsyncSession, position_id: uuid.UUID, payload: PositionUpdate
) -> PositionResponse:
    pos = await position_repo.get_by_id(db, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    updated = await position_repo.update_instance(
        db, pos, **payload.model_dump(exclude_unset=True)
    )
    return PositionResponse.model_validate(updated)


async def delete_position(db: AsyncSession, position_id: uuid.UUID) -> None:
    pos = await position_repo.get_by_id(db, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    try:
        await position_repo.delete_instance(db, pos)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Position has dependents and cannot be deleted",
        )


async def list_collateral(
    db: AsyncSession, position_id: uuid.UUID
) -> list[CollateralResponse]:
    pos = await position_repo.get_by_id(db, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    items = await collateral_repo.list_for_position(db, position_id)
    return [CollateralResponse.model_validate(i) for i in items]


async def add_collateral(
    db: AsyncSession, position_id: uuid.UUID, payload: CollateralCreate
) -> CollateralResponse:
    pos = await position_repo.get_by_id(db, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
    item = await collateral_repo.create(
        db,
        position_id=position_id,
        **payload.model_dump(),
    )
    return CollateralResponse.model_validate(item)
