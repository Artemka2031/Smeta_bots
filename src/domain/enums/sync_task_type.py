from enum import StrEnum


class SyncTaskType(StrEnum):
    APPLY_OPERATION = "apply_operation"
    DELETE_OPERATION = "delete_operation"
