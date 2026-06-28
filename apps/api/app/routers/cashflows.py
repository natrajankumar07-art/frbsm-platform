from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.cashflow import CashflowCreate, CashflowResponse, CashflowUpdate
from ..schemas.common import PagedResponse, SortDir
from ..services import cashflow as svc

router = APIRouter(prefix="/v1/cashflows", tags=["Cashflows"])


@router.get("", response_model=PagedResponse[CashflowResponse])
async def list_cashflows(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("cashflow_date"),
    sort_dir: SortDir = Query(SortDir.ASC),
    position_id: uuid.UUID | None = Query(None),
    snapshot_id: uuid.UUID | None = Query(None),
    cashflow_type: str | None = Query(None),
    cashflow_date_from: date | None = Query(None),
    cashflow_date_to: date | None = Query(None),
    time_bucket: str | None = Query(None),
    is_contractual: bool | None = Query(None),
) -> PagedResponse[CashflowResponse]:
    return await svc.list_cashflows(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        position_id=position_id,
        snapshot_id=snapshot_id,
        cashflow_type=cashflow_type,
        cashflow_date_from=cashflow_date_from,
        cashflow_date_to=cashflow_date_to,
        time_bucket=time_bucket,
        is_contractual=is_contractual,
    )


@router.post("", response_model=CashflowResponse, status_code=201)
async def create_cashflow(db: DBSession, payload: CashflowCreate) -> CashflowResponse:
    return await svc.create_cashflow(db, payload)


@router.get("/{cashflow_id}", response_model=CashflowResponse)
async def get_cashflow(db: DBSession, cashflow_id: uuid.UUID) -> CashflowResponse:
    return await svc.get_cashflow(db, cashflow_id)


@router.patch("/{cashflow_id}", response_model=CashflowResponse)
async def update_cashflow(
    db: DBSession, cashflow_id: uuid.UUID, payload: CashflowUpdate
) -> CashflowResponse:
    return await svc.update_cashflow(db, cashflow_id, payload)


@router.delete("/{cashflow_id}", status_code=204)
async def delete_cashflow(db: DBSession, cashflow_id: uuid.UUID) -> None:
    await svc.delete_cashflow(db, cashflow_id)
