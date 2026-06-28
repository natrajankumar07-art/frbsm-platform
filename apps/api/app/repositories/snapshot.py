from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.snapshot import SnapshotModel
from .base import BaseRepository


class SnapshotRepository(BaseRepository[SnapshotModel]):
    def __init__(self) -> None:
        super().__init__(SnapshotModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        reporting_date: date | None,
        status: str | None,
        frozen_by: str | None,
    ) -> tuple[list[SnapshotModel], int]:
        filters: list[Any] = []
        if reporting_date:
            filters.append(SnapshotModel.reporting_date == reporting_date)
        if status:
            filters.append(SnapshotModel.status == status)
        if frozen_by:
            filters.append(SnapshotModel.frozen_by == frozen_by)

        col = getattr(SnapshotModel, sort_by, SnapshotModel.reporting_date)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)


snapshot_repo = SnapshotRepository()
