from typing import List
from src.schemas import AuditEntry


class AuditTrailManager:
    def __init__(self):
        self._logs: List[AuditEntry] = []

    def add_entry(self, entry: AuditEntry) -> None:
        self._logs.append(entry)

    def get_logs_as_dicts(self) -> List[dict]:
        return [log.model_dump() for log in self._logs]

    def clear(self) -> None:
        self._logs.clear()