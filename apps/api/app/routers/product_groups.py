from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.product_catalog import (
    BehavioralAssumptionCreate,
    BehavioralAssumptionResponse,
    ProductGroupCreate,
    ProductGroupResponse,
    ProductGroupUpdate,
)
from ..services import product_catalog as svc

router = APIRouter(prefix="/v1/product-groups", tags=["Product Groups"])


@router.get("", response_model=PagedResponse[ProductGroupResponse])
async def list_product_groups(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("created_at"),
    sort_dir: SortDir = Query(SortDir.DESC),
    q: str | None = Query(None),
    parent_group_id: uuid.UUID | None = Query(None),
) -> PagedResponse[ProductGroupResponse]:
    return await svc.list_product_groups(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        q=q,
        parent_group_id=parent_group_id,
    )


@router.post("", response_model=ProductGroupResponse, status_code=201)
async def create_product_group(
    db: DBSession, payload: ProductGroupCreate
) -> ProductGroupResponse:
    return await svc.create_product_group(db, payload)


@router.get("/{group_id}", response_model=ProductGroupResponse)
async def get_product_group(
    db: DBSession, group_id: uuid.UUID
) -> ProductGroupResponse:
    return await svc.get_product_group(db, group_id)


@router.patch("/{group_id}", response_model=ProductGroupResponse)
async def update_product_group(
    db: DBSession, group_id: uuid.UUID, payload: ProductGroupUpdate
) -> ProductGroupResponse:
    return await svc.update_product_group(db, group_id, payload)


@router.delete("/{group_id}", status_code=204)
async def delete_product_group(db: DBSession, group_id: uuid.UUID) -> None:
    await svc.delete_product_group(db, group_id)
