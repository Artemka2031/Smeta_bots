from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import OperationStatus, OperationType
from src.infrastructure.db.base import Base, TimestampMixin


class OperationModel(TimestampMixin, Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="RESTRICT"), index=True, nullable=False)
    operation_type: Mapped[OperationType] = mapped_column(Enum(OperationType, name="operation_type"), nullable=False)
    status: Mapped[OperationStatus] = mapped_column(
        Enum(OperationStatus, name="operation_status"),
        default=OperationStatus.PENDING_SYNC,
        nullable=False,
    )
    operation_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    chapter_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    category_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subcategory_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    coming_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    creditor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    coefficient: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project = relationship("ProjectModel", back_populates="operations")
    sync_tasks = relationship("SyncTaskModel", back_populates="operation")
