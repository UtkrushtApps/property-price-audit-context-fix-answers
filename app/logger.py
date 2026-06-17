"""Tiny in-memory structured logger used so tests can inspect log output.

This stands in for a real context-aware logging framework. Each record is a
dict with a level, a message, and any structured fields passed in.
"""
from typing import Any


class CapturingLogger:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def info(self, message: str, **fields: Any) -> None:
        self.records.append({"level": "info", "message": message, **fields})

    def error(self, message: str, **fields: Any) -> None:
        self.records.append({"level": "error", "message": message, **fields})
