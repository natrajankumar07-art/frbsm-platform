from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.product_catalog import (
    BehavioralAssumptionCreate,
    BehavioralAssumptionResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from ..services import product_catalog as svc

router = APIRouter(prefix="/v1/products", tags=["Products"])


@router.get("", response_model=PagedResponse[ProductResponse])
async def list_products(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("created_at"),
    sort_dir: SortDir = Query(SortDir.DESC),
    q: str | None = Query(None),
    product_group_id: uuid.UUID | None = Query(None),
    asset_class: str | None = Query(None),
    instrument_type: str | None = Query(None),
    is_active: bool | None = Query(None),
    lcr_eligible: bool | None = Query(None),
) -> PagedResponse[ProductResponse]:
    return await svc.list_products(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        q=q,
        product_group_id=product_group_id,
        asset_class=asset_class,
        instrument_type=instrument_type,
        is_active=is_active,
        lcr_eligible=lcr_eligible,
    )


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(db: DBSession, payload: ProductCreate) -> ProductResponse:
    return await svc.create_product(db, payload)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(db: DBSession, product_id: uuid.UUID) -> ProductResponse:
    return await svc.get_product(db, product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    db: DBSession, product_id: uuid.UUID, payload: ProductUpdate
) -> ProductResponse:
    return await svc.update_product(db, product_id, payload)


@router.delete("/{product_id}", status_code=204)
async def delete_product(db: DBSession, product_id: uuid.UUID) -> None:
    await svc.delete_product(db, product_id)


@router.get(
    "/{product_id}/behavioral-assumptions",
    response_model=list[BehavioralAssumptionResponse],
)
async def list_behavioral_assumptions(
    db: DBSession, product_id: uuid.UUID
) -> list[BehavioralAssumptionResponse]:
    return await svc.list_behavioral_assumptions(db, product_id)


@router.post(
    "/{product_id}/behavioral-assumptions",
    response_model=BehavioralAssumptionResponse,
    status_code=201,
)
async def add_behavioral_assumption(
    db: DBSession, product_id: uuid.UUID, payload: BehavioralAssumptionCreate
) -> BehavioralAssumptionResponse:
    return await svc.add_behavioral_assumption(db, product_id, payload)
