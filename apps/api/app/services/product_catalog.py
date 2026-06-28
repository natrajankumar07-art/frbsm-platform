from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.product_catalog import (
    behavioral_assumption_repo,
    product_group_repo,
    product_repo,
)
from ..schemas.common import PagedResponse, SortDir
from ..schemas.product_catalog import (
    BehavioralAssumptionCreate,
    BehavioralAssumptionResponse,
    ProductCreate,
    ProductGroupCreate,
    ProductGroupResponse,
    ProductGroupUpdate,
    ProductResponse,
    ProductUpdate,
)

_GROUP_SORT = {"name", "code", "created_at", "updated_at"}
_PRODUCT_SORT = {"name", "code", "asset_class", "instrument_type", "created_at", "updated_at"}


async def list_product_groups(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    q: str | None,
    parent_group_id: uuid.UUID | None,
) -> PagedResponse[ProductGroupResponse]:
    if sort_by not in _GROUP_SORT:
        sort_by = "created_at"
    items, total = await product_group_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        q=q,
        parent_group_id=parent_group_id,
    )
    return PagedResponse.create(
        [ProductGroupResponse.model_validate(i) for i in items], total, page, size
    )


async def get_product_group(
    db: AsyncSession, group_id: uuid.UUID
) -> ProductGroupResponse:
    group = await product_group_repo.get_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Product group not found")
    return ProductGroupResponse.model_validate(group)


async def create_product_group(
    db: AsyncSession, payload: ProductGroupCreate
) -> ProductGroupResponse:
    try:
        group = await product_group_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Product group code already exists")
    return ProductGroupResponse.model_validate(group)


async def update_product_group(
    db: AsyncSession, group_id: uuid.UUID, payload: ProductGroupUpdate
) -> ProductGroupResponse:
    group = await product_group_repo.get_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Product group not found")
    updated = await product_group_repo.update_instance(
        db, group, **payload.model_dump(exclude_unset=True)
    )
    return ProductGroupResponse.model_validate(updated)


async def delete_product_group(db: AsyncSession, group_id: uuid.UUID) -> None:
    group = await product_group_repo.get_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Product group not found")
    try:
        await product_group_repo.delete_instance(db, group)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Product group has dependents and cannot be deleted"
        )


async def list_products(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    q: str | None,
    product_group_id: uuid.UUID | None,
    asset_class: str | None,
    instrument_type: str | None,
    is_active: bool | None,
    lcr_eligible: bool | None,
) -> PagedResponse[ProductResponse]:
    if sort_by not in _PRODUCT_SORT:
        sort_by = "created_at"
    items, total = await product_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        q=q,
        product_group_id=product_group_id,
        asset_class=asset_class,
        instrument_type=instrument_type,
        is_active=is_active,
        lcr_eligible=lcr_eligible,
    )
    return PagedResponse.create(
        [ProductResponse.model_validate(i) for i in items], total, page, size
    )


async def get_product(db: AsyncSession, product_id: uuid.UUID) -> ProductResponse:
    product = await product_repo.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


async def create_product(db: AsyncSession, payload: ProductCreate) -> ProductResponse:
    try:
        product = await product_repo.create(db, **payload.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Product code already exists")
    return ProductResponse.model_validate(product)


async def update_product(
    db: AsyncSession, product_id: uuid.UUID, payload: ProductUpdate
) -> ProductResponse:
    product = await product_repo.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = await product_repo.update_instance(
        db, product, **payload.model_dump(exclude_unset=True)
    )
    return ProductResponse.model_validate(updated)


async def delete_product(db: AsyncSession, product_id: uuid.UUID) -> None:
    product = await product_repo.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        await product_repo.delete_instance(db, product)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Product has dependents and cannot be deleted"
        )


async def list_behavioral_assumptions(
    db: AsyncSession, product_id: uuid.UUID
) -> list[BehavioralAssumptionResponse]:
    product = await product_repo.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    items = await behavioral_assumption_repo.list_for_product(db, product_id)
    return [BehavioralAssumptionResponse.model_validate(i) for i in items]


async def add_behavioral_assumption(
    db: AsyncSession, product_id: uuid.UUID, payload: BehavioralAssumptionCreate
) -> BehavioralAssumptionResponse:
    product = await product_repo.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    item = await behavioral_assumption_repo.create(
        db, product_id=product_id, **payload.model_dump()
    )
    return BehavioralAssumptionResponse.model_validate(item)
