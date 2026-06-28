from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self._model = model

    async def get_by_id(self, db: AsyncSession, id: uuid.UUID) -> ModelT | None:
        stmt = select(self._model).where(
            self._model.id == id  # type: ignore[attr-defined]
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    async def _count(self, db: AsyncSession, *where_clauses: Any) -> int:
        stmt = select(func.count()).select_from(self._model)  # type: ignore[arg-type]
        for clause in where_clauses:
            stmt = stmt.where(clause)
        return (await db.execute(stmt)).scalar_one()

    async def _list(
        self,
        db: AsyncSession,
        *where_clauses: Any,
        page: int,
        size: int,
        order_by: Any,
    ) -> tuple[list[ModelT], int]:
        total = await self._count(db, *where_clauses)
        offset = (page - 1) * size
        stmt = select(self._model)
        for clause in where_clauses:
            stmt = stmt.where(clause)
        stmt = stmt.order_by(order_by).offset(offset).limit(size)
        items = list((await db.execute(stmt)).scalars().all())
        return items, total

    async def create(self, db: AsyncSession, **kwargs: Any) -> ModelT:
        instance = self._model(**kwargs)  # type: ignore[call-arg]
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def update_instance(
        self, db: AsyncSession, instance: ModelT, **kwargs: Any
    ) -> ModelT:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def delete_instance(self, db: AsyncSession, instance: ModelT) -> None:
        await db.delete(instance)
        await db.flush()
