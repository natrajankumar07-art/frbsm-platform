from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.cashflow import CashflowModel
from .base import BaseRepository


class CashflowRepository(BaseRepository[CashflowModel]):
    def __init__(self) -> None:
        super().__init__(CashflowModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        position_id: uuid.UUID | None,
        snapshot_id: uuid.UUID | None,
        cashflow_type: str | None,
        cashflow_date_from: date | None,
        cashflow_date_to: date | None,
        time_bucket: str | None,
        is_contractual: bool | None,
    ) -> tuple[list[CashflowModel], int]:
        filters: list[Any] = []
        if position_id:
            filters.append(CashflowModel.position_id == position_id)
        if snapshot_id:
            filters.append(CashflowModel.snapshot_id == snapshot_id)
        if cashflow_type:
            filters.append(CashflowModel.cashflow_type == cashflow_type)
        if cashflow_date_from:
            filters.append(CashflowModel.cashflow_date >= cashflow_date_from)
        if cashflow_date_to:
            filters.append(CashflowModel.cashflow_date <= cashflow_date_to)
        if time_bucket:
            filters.append(CashflowModel.time_bucket == time_bucket)
        if is_contractual is not None:
            filters.append(CashflowModel.is_contractual == is_contractual)

        col = getattr(CashflowModel, sort_by, CashflowModel.cashflow_date)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)


cashflow_repo = CashflowRepository()
