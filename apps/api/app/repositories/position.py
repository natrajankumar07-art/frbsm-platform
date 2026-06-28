from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.position import CollateralModel, PositionModel
from .base import BaseRepository


class PositionRepository(BaseRepository[PositionModel]):
    def __init__(self) -> None:
        super().__init__(PositionModel)

    async def get_by_id(  # type: ignore[override]
        self, db: AsyncSession, id: uuid.UUID, reporting_date: date | None = None
    ) -> PositionModel | None:
        stmt = select(PositionModel).where(PositionModel.id == id)
        if reporting_date:
            stmt = stmt.where(PositionModel.reporting_date == reporting_date)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        counterparty_id: uuid.UUID | None,
        reporting_date: date | None,
        asset_class: str | None,
        currency: str | None,
        status: str | None,
        hqla_level: str | None,
        ifrs9_stage: str | None,
    ) -> tuple[list[PositionModel], int]:
        filters: list[Any] = []
        if counterparty_id:
            filters.append(PositionModel.counterparty_id == counterparty_id)
        if reporting_date:
            filters.append(PositionModel.reporting_date == reporting_date)
        if asset_class:
            filters.append(PositionModel.asset_class == asset_class)
        if currency:
            filters.append(PositionModel.currency == currency)
        if status:
            filters.append(PositionModel.status == status)
        if hqla_level:
            filters.append(PositionModel.hqla_level == hqla_level)
        if ifrs9_stage:
            filters.append(PositionModel.ifrs9_stage == ifrs9_stage)

        col = getattr(PositionModel, sort_by, PositionModel.created_at)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)

    async def delete_instance(self, db: AsyncSession, instance: PositionModel) -> None:
        await db.delete(instance)
        await db.flush()


class CollateralRepository(BaseRepository[CollateralModel]):
    def __init__(self) -> None:
        super().__init__(CollateralModel)

    async def list_for_position(
        self, db: AsyncSession, position_id: uuid.UUID
    ) -> list[CollateralModel]:
        stmt = (
            select(CollateralModel)
            .where(CollateralModel.position_id == position_id)
            .order_by(CollateralModel.created_at.desc())
        )
        return list((await db.execute(stmt)).scalars().all())


position_repo = PositionRepository()
collateral_repo = CollateralRepository()
