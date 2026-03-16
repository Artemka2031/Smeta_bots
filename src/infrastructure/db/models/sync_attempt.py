from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import SyncStatus
from src.infrastructure.db.base import Base, TimestampMixin


class SyncAttemptModel(TimestampMixin, Base):
    __tablename__ = "sync_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sync_task_id: Mapped[int] = mapped_column(ForeignKey("sync_tasks.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus, name="sync_attempt_status"), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    sync_task = relationship("SyncTaskModel", back_populates="attempts")
