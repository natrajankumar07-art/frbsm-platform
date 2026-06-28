from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.legal_entity import EntityCapitalRequirementModel, LegalEntityModel
from .base import BaseRepository


class LegalEntityRepository(BaseRepository[LegalEntityModel]):
    def __init__(self) -> None:
        super().__init__(LegalEntityModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        q: str | None,
        jurisdiction: str | None,
        entity_type: str | None,
        is_consolidated: bool | None,
        is_reporting_entity: bool | None,
    ) -> tuple[list[LegalEntityModel], int]:
        filters: list[Any] = []
        if q:
            filters.append(
                or_(
                    LegalEntityModel.name.ilike(f"%{q}%"),
                    LegalEntityModel.code.ilike(f"%{q}%"),
                    LegalEntityModel.lei.ilike(f"%{q}%"),
                )
            )
        if jurisdiction:
            filters.append(LegalEntityModel.jurisdiction == jurisdiction)
        if entity_type:
            filters.append(LegalEntityModel.entity_type == entity_type)
        if is_consolidated is not None:
            filters.append(LegalEntityModel.is_consolidated == is_consolidated)
        if is_reporting_entity is not None:
            filters.append(LegalEntityModel.is_reporting_entity == is_reporting_entity)

        col = getattr(LegalEntityModel, sort_by, LegalEntityModel.created_at)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)

    async def get_by_code(self, db: AsyncSession, code: str) -> LegalEntityModel | None:
        stmt = select(LegalEntityModel).where(LegalEntityModel.code == code)
        return (await db.execute(stmt)).scalar_one_or_none()


class CapitalRequirementRepository(BaseRepository[EntityCapitalRequirementModel]):
    def __init__(self) -> None:
        super().__init__(EntityCapitalRequirementModel)

    async def list_for_entity(
        self, db: AsyncSession, entity_id: uuid.UUID
    ) -> list[EntityCapitalRequirementModel]:
        stmt = (
            select(EntityCapitalRequirementModel)
            .where(EntityCapitalRequirementModel.entity_id == entity_id)
            .order_by(EntityCapitalRequirementModel.effective_from.desc())
        )
        return list((await db.execute(stmt)).scalars().all())


legal_entity_repo = LegalEntityRepository()
capital_req_repo = CapitalRequirementRepository()
