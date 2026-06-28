from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.snapshot import SnapshotCreate, SnapshotResponse, SnapshotUpdate
from ..services import snapshot as svc

router = APIRouter(prefix="/v1/snapshots", tags=["Balance Sheet Snapshots"])


@router.get("", response_model=PagedResponse[SnapshotResponse])
async def list_snapshots(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("reporting_date"),
    sort_dir: SortDir = Query(SortDir.DESC),
    reporting_date: date | None = Query(None),
    status: str | None = Query(None),
    frozen_by: str | None = Query(None),
) -> PagedResponse[SnapshotResponse]:
    return await svc.list_snapshots(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        reporting_date=reporting_date,
        status=status,
        frozen_by=frozen_by,
    )


@router.post("", response_model=SnapshotResponse, status_code=201)
async def create_snapshot(db: DBSession, payload: SnapshotCreate) -> SnapshotResponse:
    return await svc.create_snapshot(db, payload)


@router.get("/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(db: DBSession, snapshot_id: uuid.UUID) -> SnapshotResponse:
    return await svc.get_snapshot(db, snapshot_id)


@router.patch("/{snapshot_id}", response_model=SnapshotResponse)
async def update_snapshot(
    db: DBSession, snapshot_id: uuid.UUID, payload: SnapshotUpdate
) -> SnapshotResponse:
    return await svc.update_snapshot(db, snapshot_id, payload)


@router.delete("/{snapshot_id}", status_code=204)
async def delete_snapshot(db: DBSession, snapshot_id: uuid.UUID) -> None:
    await svc.delete_snapshot(db, snapshot_id)
