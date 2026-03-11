"""TimeManager: gestion du temps indépendante de pygame."""

import logging
import time as _time

logger = logging.getLogger(__name__)


class TimeManager:
    def __init__(self) -> None:
        self._last_time: float = _time.time()
        self._ticks: float = 0.0
        self._dt: float = 0.0

    def tick(self) -> float:
        now = _time.time()
        self._dt = now - self._last_time
        self._last_time = now
        self._ticks += self._dt * 1000
        if self._dt > 0.1:
            logger.debug("Frame time spike: %.0f ms", self._dt * 1000)
        return self._dt

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def ticks(self) -> float:
        """Temps écoulé en millisecondes depuis la création."""
        return self._ticks
