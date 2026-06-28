from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.product_catalog import (
    ProductBehavioralAssumptionModel,
    ProductGroupModel,
    ProductModel,
)
from .base import BaseRepository


class ProductGroupRepository(BaseRepository[ProductGroupModel]):
    def __init__(self) -> None:
        super().__init__(ProductGroupModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        q: str | None,
        parent_group_id: uuid.UUID | None,
    ) -> tuple[list[ProductGroupModel], int]:
        filters: list[Any] = []
        if q:
            filters.append(
                or_(
                    ProductGroupModel.name.ilike(f"%{q}%"),
                    ProductGroupModel.code.ilike(f"%{q}%"),
                )
            )
        if parent_group_id is not None:
            filters.append(ProductGroupModel.parent_group_id == parent_group_id)

        col = getattr(ProductGroupModel, sort_by, ProductGroupModel.created_at)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)


class ProductRepository(BaseRepository[ProductModel]):
    def __init__(self) -> None:
        super().__init__(ProductModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        q: str | None,
        product_group_id: uuid.UUID | None,
        asset_class: str | None,
        instrument_type: str | None,
        is_active: bool | None,
        lcr_eligible: bool | None,
    ) -> tuple[list[ProductModel], int]:
        filters: list[Any] = []
        if q:
            filters.append(
                or_(
                    ProductModel.name.ilike(f"%{q}%"),
                    ProductModel.code.ilike(f"%{q}%"),
                )
            )
        if product_group_id:
            filters.append(ProductModel.product_group_id == product_group_id)
        if asset_class:
            filters.append(ProductModel.asset_class == asset_class)
        if instrument_type:
            filters.append(ProductModel.instrument_type == instrument_type)
        if is_active is not None:
            filters.append(ProductModel.is_active == is_active)
        if lcr_eligible is not None:
            filters.append(ProductModel.lcr_eligible == lcr_eligible)

        col = getattr(ProductModel, sort_by, ProductModel.created_at)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)


class BehavioralAssumptionRepository(BaseRepository[ProductBehavioralAssumptionModel]):
    def __init__(self) -> None:
        super().__init__(ProductBehavioralAssumptionModel)

    async def list_for_product(
        self, db: AsyncSession, product_id: uuid.UUID
    ) -> list[ProductBehavioralAssumptionModel]:
        stmt = (
            select(ProductBehavioralAssumptionModel)
            .where(ProductBehavioralAssumptionModel.product_id == product_id)
            .order_by(ProductBehavioralAssumptionModel.effective_from.desc())
        )
        return list((await db.execute(stmt)).scalars().all())


product_group_repo = ProductGroupRepository()
product_repo = ProductRepository()
behavioral_assumption_repo = BehavioralAssumptionRepository()
