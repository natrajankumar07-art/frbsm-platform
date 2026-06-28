from __future__ import annotations

import math
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SortDir(StrEnum):
    ASC = "asc"
    DESC = "desc"


class PageMeta(BaseModel):
    page: int
    size: int
    total: int
    pages: int


class PagedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, size: int
    ) -> PagedResponse[T]:
        pages = max(1, math.ceil(total / size)) if size > 0 else 1
        return cls(
            items=items,
            meta=PageMeta(page=page, size=size, total=total, pages=pages),
        )
