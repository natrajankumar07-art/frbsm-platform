from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.cashflow import cashflow_repo
from ..schemas.cashflow import CashflowCreate, CashflowResponse, CashflowUpdate
from ..schemas.common import PagedResponse, SortDir

_ALLOWED_SORT_BY = {
    "cashflow_date", "cashflow_type", "amount", "time_bucket", "created_at", "updated_at"
}


async def list_cashflows(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    position_id: uuid.UUID | None,
    snapshot_id: uuid.UUID | None,
    cashflow_type: str | None,
    cashflow_date_from: date | None,
    cashflow_date_to: date | None,
    time_bucket: str | None,
    is_contractual: bool | None,
) -> PagedResponse[CashflowResponse]:
    if sort_by not in _ALLOWED_SORT_BY:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by '{sort_by}'. Allowed: {sorted(_ALLOWED_SORT_BY)}")
    items, total = await cashflow_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        position_id=position_id,
        snapshot_id=snapshot_id,
        cashflow_type=cashflow_type,
        cashflow_date_from=cashflow_date_from,
        cashflow_date_to=cashflow_date_to,
        time_bucket=time_bucket,
        is_contractual=is_contractual,
    )
    return PagedResponse.create(
        [CashflowResponse.model_validate(i) for i in items], total, page, size
    )


async def get_cashflow(db: AsyncSession, cashflow_id: uuid.UUID) -> CashflowResponse:
    cf = await cashflow_repo.get_by_id(db, cashflow_id)
    if not cf:
        raise HTTPException(status_code=404, detail="Cashflow not found")
    return CashflowResponse.model_validate(cf)


async def create_cashflow(
    db: AsyncSession, payload: CashflowCreate
) -> CashflowResponse:
    try:
        cf = await cashflow_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Cashflow conflicts with existing data"
        )
    return CashflowResponse.model_validate(cf)


async def update_cashflow(
    db: AsyncSession, cashflow_id: uuid.UUID, payload: CashflowUpdate
) -> CashflowResponse:
    cf = await cashflow_repo.get_by_id(db, cashflow_id)
    if not cf:
        raise HTTPException(status_code=404, detail="Cashflow not found")
    updated = await cashflow_repo.update_instance(
        db, cf, **payload.model_dump(exclude_unset=True)
    )
    return CashflowResponse.model_validate(updated)


async def delete_cashflow(db: AsyncSession, cashflow_id: uuid.UUID) -> None:
    cf = await cashflow_repo.get_by_id(db, cashflow_id)
    if not cf:
        raise HTTPException(status_code=404, detail="Cashflow not found")
    await cashflow_repo.delete_instance(db, cf)
