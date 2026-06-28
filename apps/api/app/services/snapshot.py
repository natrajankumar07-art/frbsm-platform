from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.snapshot import snapshot_repo
from ..schemas.common import PagedResponse, SortDir
from ..schemas.snapshot import SnapshotCreate, SnapshotResponse, SnapshotUpdate

_ALLOWED_SORT_BY = {"reporting_date", "status", "frozen_at", "created_at", "updated_at"}
_IMMUTABLE_STATUSES = {"locked", "filed"}


async def list_snapshots(
    db: AsyncSession,
    *,
    page: int,
    size: int,
    sort_by: str,
    sort_dir: SortDir,
    reporting_date: date | None,
    status: str | None,
    frozen_by: str | None,
) -> PagedResponse[SnapshotResponse]:
    if sort_by not in _ALLOWED_SORT_BY:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by '{sort_by}'. Allowed: {sorted(_ALLOWED_SORT_BY)}")
    items, total = await snapshot_repo.list(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir.value,
        reporting_date=reporting_date,
        status=status,
        frozen_by=frozen_by,
    )
    return PagedResponse.create(
        [SnapshotResponse.model_validate(i) for i in items], total, page, size
    )


async def get_snapshot(db: AsyncSession, snapshot_id: uuid.UUID) -> SnapshotResponse:
    snap = await snapshot_repo.get_by_id(db, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return SnapshotResponse.model_validate(snap)


async def create_snapshot(
    db: AsyncSession, payload: SnapshotCreate
) -> SnapshotResponse:
    try:
        snap = await snapshot_repo.create(
            db,
            frozen_at=datetime.now(tz=timezone.utc),
            **payload.model_dump(),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Snapshot conflicts with existing data"
        )
    return SnapshotResponse.model_validate(snap)


async def update_snapshot(
    db: AsyncSession, snapshot_id: uuid.UUID, payload: SnapshotUpdate
) -> SnapshotResponse:
    snap = await snapshot_repo.get_by_id(db, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    if snap.status in _IMMUTABLE_STATUSES:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot modify a snapshot in '{snap.status}' status",
        )
    updated = await snapshot_repo.update_instance(
        db, snap, **payload.model_dump(exclude_unset=True)
    )
    return SnapshotResponse.model_validate(updated)


async def delete_snapshot(db: AsyncSession, snapshot_id: uuid.UUID) -> None:
    snap = await snapshot_repo.get_by_id(db, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    if snap.status in _IMMUTABLE_STATUSES:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete a snapshot in '{snap.status}' status",
        )
    try:
        await snapshot_repo.delete_instance(db, snap)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Snapshot has dependents and cannot be deleted",
        )
