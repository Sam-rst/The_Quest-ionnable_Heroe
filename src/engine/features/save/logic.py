"""SaveManager générique — indépendant du format de stockage."""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class SaveBackend(ABC):
    @abstractmethod
    def load(self) -> dict: ...

    @abstractmethod
    def save(self, data: dict) -> None: ...

    @abstractmethod
    def delete(self) -> None: ...

    @abstractmethod
    def exists(self) -> bool: ...


class SaveManager:
    def __init__(self, backend: SaveBackend) -> None:
        self.backend = backend
        self._data: dict | None = None

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = self.backend.load() if self.backend.exists() else {}
        return self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def save(self) -> None:
        self.backend.save(self.data)
        logger.info("Save written")

    def delete(self) -> None:
        self.backend.delete()
        self._data = None
        logger.info("Save deleted")

    def reload(self) -> None:
        self._data = None
        logger.info("Save reloaded")
