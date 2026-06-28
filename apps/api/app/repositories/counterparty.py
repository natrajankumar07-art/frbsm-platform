from __future__ import annotations

from typing import Any

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.counterparty import CounterpartyModel
from .base import BaseRepository


class CounterpartyRepository(BaseRepository[CounterpartyModel]):
    def __init__(self) -> None:
        super().__init__(CounterpartyModel)

    async def list(
        self,
        db: AsyncSession,
        *,
        page: int,
        size: int,
        sort_by: str,
        sort_dir: str,
        q: str | None,
        sector: str | None,
        jurisdiction: str | None,
        rating: str | None,
        is_financial_institution: bool | None,
    ) -> tuple[list[CounterpartyModel], int]:
        filters: list[Any] = []
        if q:
            filters.append(
                or_(
                    CounterpartyModel.name.ilike(f"%{q}%"),
                    CounterpartyModel.lei.ilike(f"%{q}%"),
                )
            )
        if sector:
            filters.append(CounterpartyModel.sector == sector)
        if jurisdiction:
            filters.append(CounterpartyModel.jurisdiction == jurisdiction)
        if rating:
            filters.append(CounterpartyModel.rating == rating)
        if is_financial_institution is not None:
            filters.append(
                CounterpartyModel.is_financial_institution == is_financial_institution
            )

        col = getattr(CounterpartyModel, sort_by, CounterpartyModel.created_at)
        order = col.asc() if sort_dir == "asc" else col.desc()
        return await self._list(db, *filters, page=page, size=size, order_by=order)


counterparty_repo = CounterpartyRepository()
