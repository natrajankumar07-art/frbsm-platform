from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from ..dependencies import DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.counterparty import (
    CounterpartyCreate,
    CounterpartyResponse,
    CounterpartyUpdate,
)
from ..services import counterparty as svc

router = APIRouter(prefix="/v1/counterparties", tags=["Counterparties"])


@router.get("", response_model=PagedResponse[CounterpartyResponse])
async def list_counterparties(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("created_at"),
    sort_dir: SortDir = Query(SortDir.DESC),
    q: str | None = Query(None),
    sector: str | None = Query(None),
    jurisdiction: str | None = Query(None),
    rating: str | None = Query(None),
    is_financial_institution: bool | None = Query(None),
) -> PagedResponse[CounterpartyResponse]:
    return await svc.list_counterparties(
        db,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        q=q,
        sector=sector,
        jurisdiction=jurisdiction,
        rating=rating,
        is_financial_institution=is_financial_institution,
    )


@router.post("", response_model=CounterpartyResponse, status_code=201)
async def create_counterparty(
    db: DBSession, payload: CounterpartyCreate
) -> CounterpartyResponse:
    return await svc.create_counterparty(db, payload)


@router.get("/{counterparty_id}", response_model=CounterpartyResponse)
async def get_counterparty(
    db: DBSession, counterparty_id: uuid.UUID
) -> CounterpartyResponse:
    return await svc.get_counterparty(db, counterparty_id)


@router.patch("/{counterparty_id}", response_model=CounterpartyResponse)
async def update_counterparty(
    db: DBSession, counterparty_id: uuid.UUID, payload: CounterpartyUpdate
) -> CounterpartyResponse:
    return await svc.update_counterparty(db, counterparty_id, payload)


@router.delete("/{counterparty_id}", status_code=204)
async def delete_counterparty(db: DBSession, counterparty_id: uuid.UUID) -> None:
    await svc.delete_counterparty(db, counterparty_id)
