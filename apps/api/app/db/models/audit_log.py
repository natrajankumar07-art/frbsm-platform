"""
Audit log ORM model.

DESIGN NOTE: This table is append-only. The ORM model intentionally exposes
no update() or delete() methods. The application layer (AuditLogger in
platform-audit) enforces INSERT-only semantics.

Hash-chaining: each entry stores a SHA-256 of its own content plus the
previous entry's hash, forming a tamper-evident chain. The chain is verified
nightly by the determinism CI job.
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, UUIDPrimaryKeyMixin


class AuditLogEntry(UUIDPrimaryKeyMixin, Base):
    """
    Immutable audit record. No TimestampMixin — created_at is the only timestamp
    and must be set at insert time; there is no updated_at for an append-only table.
    """

    __tablename__ = "audit_log"

    # When this entry was written
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Who performed the action
    user_id: Mapped[str] = mapped_column(String(200), nullable=False)
    user_role: Mapped[str] = mapped_column(String(20), nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6-safe

    # What happened
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Distributed trace
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Hash chain: SHA-256(this_entry_content + prev_hash)
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # "0"*64 for first entry

    # Sequence number for ordering without relying on timestamps
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_audit_log_created_at", "created_at"),
        Index("ix_audit_log_user_id", "user_id"),
        Index("ix_audit_log_action", "action"),
        Index("ix_audit_log_resource", "resource_type", "resource_id"),
        Index("ix_audit_log_sequence", "sequence_number"),
    )
