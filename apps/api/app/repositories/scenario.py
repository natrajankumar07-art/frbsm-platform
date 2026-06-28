from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.scenario import ScenarioModel, ScenarioParameterSetModel
from .base import BaseRepository


class ScenarioRepository(BaseRepository[ScenarioModel]):
    def __init__(self) -> None:
        super().__init__(ScenarioModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        q: str | None,
        scenario_type: str | None,
        severity: str | None,
        is_regulatory: bool | None,
        is_active: bool | None,
    ) -> tuple[list[ScenarioModel], int]:
        filters: list[Any] = []
        if q:
            filters.append(
                or_(
                    ScenarioModel.name.ilike(f"%{q}%"),
                    ScenarioModel.code.ilike(f"%{q}%"),
                )
            )
        if scenario_type:
            filters.append(ScenarioModel.scenario_type == scenario_type)
        if severity:
            filters.append(ScenarioModel.severity == severity)
        if is_regulatory is not None:
            filters.append(ScenarioModel.is_regulatory == is_regulatory)
        if is_active is not None:
            filters.append(ScenarioModel.is_active == is_active)

        col = getattr(ScenarioModel, sort_by, ScenarioModel.created_at)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)

    async def get_by_code(self, db: AsyncSession, code: str) -> ScenarioModel | None:
        stmt = select(ScenarioModel).where(ScenarioModel.code == code)
        return (await db.execute(stmt)).scalar_one_or_none()


class ScenarioParameterSetRepository(BaseRepository[ScenarioParameterSetModel]):
    def __init__(self) -> None:
        super().__init__(ScenarioParameterSetModel)

    async def list_for_scenario(
        self, db: AsyncSession, scenario_id: uuid.UUID
    ) -> list[ScenarioParameterSetModel]:
        stmt = (
            select(ScenarioParameterSetModel)
            .where(ScenarioParameterSetModel.scenario_id == scenario_id)
            .order_by(ScenarioParameterSetModel.parameter_type)
        )
        return list((await db.execute(stmt)).scalars().all())


scenario_repo = ScenarioRepository()
scenario_param_repo = ScenarioParameterSetRepository()
