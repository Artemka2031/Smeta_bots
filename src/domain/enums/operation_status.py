from enum import StrEnum


class OperationStatus(StrEnum):
    PENDING_SYNC = "pending_sync"
    SYNCED = "synced"
    SYNC_FAILED = "sync_failed"
    DELETED = "deleted"
