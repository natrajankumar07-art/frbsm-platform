"""Counterparty and group structure domain models."""

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .enums import CurrencyCode, Jurisdiction, RatingGrade


class Counterparty(BaseModel):
    """
    A legal entity that is a counterparty to one or more balance-sheet positions.

    The `lei` (Legal Entity Identifier) is the primary deduplication key for
    counterparties arriving from multiple source systems.
    """

    model_config = {"frozen": True}

    id: UUID
    name: str = Field(..., min_length=1, max_length=500)
    lei: str | None = Field(None, pattern=r"^[A-Z0-9]{18}[0-9]{2}$")
    sector: str = Field(..., min_length=1, max_length=100)
    industry: str | None = Field(None, max_length=100)
    geography: str = Field(..., pattern=r"^[A-Z]{2}$")  # ISO 3166-1 alpha-2
    jurisdiction: Jurisdiction
    group_id: UUID | None = None
    group_name: str | None = Field(None, max_length=500)
    rating: RatingGrade = RatingGrade.UNRATED
    is_financial_institution: bool = False
    is_sovereign: bool = False
    is_large_exposure: bool = False  # Exposure >10% of eligible capital

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Counterparty name cannot be blank")
        return v.strip()


class GroupStructure(BaseModel):
    """Consolidated group containing multiple legal entities."""

    model_config = {"frozen": True}

    group_id: UUID
    group_name: str = Field(..., min_length=1, max_length=500)
    parent_entity_id: UUID | None = None
    jurisdiction: Jurisdiction
    consolidated_for_reporting: bool = True
    members: list[UUID] = Field(default_factory=list)
    functional_currencies: list[CurrencyCode] = Field(default_factory=list)
