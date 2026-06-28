from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.stress_test import (
    StressPositionImpactModel,
    StressTestResultModel,
    StressTestRunModel,
)
from .base import BaseRepository


class StressTestRunRepository(BaseRepository[StressTestRunModel]):
    def __init__(self) -> None:
        super().__init__(StressTestRunModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        snapshot_id: uuid.UUID | None,
        scenario_id: uuid.UUID | None,
        status: str | None,
        run_type: str | None,
    ) -> tuple[list[StressTestRunModel], int]:
        filters: list[Any] = []
        if snapshot_id:
            filters.append(StressTestRunModel.snapshot_id == snapshot_id)
        if scenario_id:
            filters.append(StressTestRunModel.scenario_id == scenario_id)
        if status:
            filters.append(StressTestRunModel.status == status)
        if run_type:
            filters.append(StressTestRunModel.run_type == run_type)

        col = getattr(StressTestRunModel, sort_by, StressTestRunModel.created_at)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)


class StressTestResultRepository(BaseRepository[StressTestResultModel]):
    def __init__(self) -> None:
        super().__init__(StressTestResultModel)

    async def list_for_run(
        self, db: AsyncSession, stress_run_id: uuid.UUID
    ) -> list[StressTestResultModel]:
        stmt = (
            select(StressTestResultModel)
            .where(StressTestResultModel.stress_run_id == stress_run_id)
            .order_by(StressTestResultModel.metric_name)
        )
        return list((await db.execute(stmt)).scalars().all())


class StressPositionImpactRepository(BaseRepository[StressPositionImpactModel]):
    def __init__(self) -> None:
        super().__init__(StressPositionImpactModel)

    async def list_for_run(
        self, db: AsyncSession, stress_run_id: uuid.UUID
    ) -> list[StressPositionImpactModel]:
        stmt = (
            select(StressPositionImpactModel)
            .where(StressPositionImpactModel.stress_run_id == stress_run_id)
            .order_by(StressPositionImpactModel.metric_name)
        )
        return list((await db.execute(stmt)).scalars().all())


stress_run_repo = StressTestRunRepository()
stress_result_repo = StressTestResultRepository()
stress_impact_repo = StressPositionImpactRepository()
