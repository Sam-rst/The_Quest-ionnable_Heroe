"""EventBus: publish/subscribe pour découpler les features entre elles."""

from __future__ import annotations
from typing import Any, Callable


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        self._listeners.setdefault(event_type, []).append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)

    def emit(self, event_type: str, **data: Any) -> None:
        for callback in self._listeners.get(event_type, []):
            callback(**data)
