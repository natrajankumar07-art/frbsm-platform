from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.position import (
    CollateralCreate,
    CollateralResponse,
    PositionCreate,
    PositionResponse,
    PositionUpdate,
)
from ..services import position as svc

router = APIRouter(prefix="/v1/positions", tags=["Positions"])


@router.get("", response_model=PagedResponse[PositionResponse])
async def list_positions(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("created_at"),
    sort_dir: SortDir = Query(SortDir.DESC),
    counterparty_id: uuid.UUID | None = Query(None),
    reporting_date: date | None = Query(None),
    asset_class: str | None = Query(None),
    currency: str | None = Query(None),
    status: str | None = Query(None),
    hqla_level: str | None = Query(None),
    ifrs9_stage: str | None = Query(None),
) -> PagedResponse[PositionResponse]:
    return await svc.list_positions(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        counterparty_id=counterparty_id,
        reporting_date=reporting_date,
        asset_class=asset_class,
        currency=currency,
        status=status,
        hqla_level=hqla_level,
        ifrs9_stage=ifrs9_stage,
    )


@router.post("", response_model=PositionResponse, status_code=201)
async def create_position(db: DBSession, payload: PositionCreate) -> PositionResponse:
    return await svc.create_position(db, payload)


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(db: DBSession, position_id: uuid.UUID) -> PositionResponse:
    return await svc.get_position(db, position_id)


@router.patch("/{position_id}", response_model=PositionResponse)
async def update_position(
    db: DBSession, position_id: uuid.UUID, payload: PositionUpdate
) -> PositionResponse:
    return await svc.update_position(db, position_id, payload)


@router.delete("/{position_id}", status_code=204)
async def delete_position(db: DBSession, position_id: uuid.UUID) -> None:
    await svc.delete_position(db, position_id)


@router.get("/{position_id}/collateral", response_model=list[CollateralResponse])
async def list_collateral(
    db: DBSession, position_id: uuid.UUID
) -> list[CollateralResponse]:
    return await svc.list_collateral(db, position_id)


@router.post(
    "/{position_id}/collateral", response_model=CollateralResponse, status_code=201
)
async def add_collateral(
    db: DBSession, position_id: uuid.UUID, payload: CollateralCreate
) -> CollateralResponse:
    return await svc.add_collateral(db, position_id, payload)
