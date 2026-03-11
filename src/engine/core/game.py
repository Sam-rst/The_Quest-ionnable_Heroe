"""Game: boucle principale, feature registry, world et event bus."""

from __future__ import annotations
import logging

from engine.core.world import World
from engine.core.event_bus import EventBus
from engine.core.system import System, Feature
from engine.core.time_manager import TimeManager

logger = logging.getLogger(__name__)


class Game:
    def __init__(self) -> None:
        self.world = World()
        self.event_bus = EventBus()
        self.time = TimeManager()
        self._systems: list[System] = []
        self._features: list[Feature] = []
        self._renderers: list = []
        self.running = False
        self.settings: dict = {}

    def add_system(self, system: System) -> None:
        system.game = self
        self._systems.append(system)
        system.on_enter()
        logger.debug("System registered: %s", type(system).__name__)

    def add_feature(self, feature: Feature) -> None:
        feature.game = self
        self._features.append(feature)
        feature.register(self)

    def add_renderer(self, renderer) -> None:
        self._renderers.append(renderer)

    def update(self, dt: float) -> None:
        for system in self._systems:
            system.update(dt)

    def render(self) -> None:
        for renderer in self._renderers:
            renderer.render()

    def quit(self) -> None:
        logger.info("Game quit requested")
        self.running = False
