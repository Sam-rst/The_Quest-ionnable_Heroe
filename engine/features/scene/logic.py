"""SceneManager: gestion d'une pile de scènes (push/pop)."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.core.game import Game


class Scene(ABC):
    game: Game | None = None

    @abstractmethod
    def on_enter(self) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def render(self) -> None: ...

    def on_exit(self) -> None: ...

    def handle_events(self, events: list) -> None: ...


class SceneManager:
    def __init__(self, game: Game) -> None:
        self.game = game
        self._stack: list[Scene] = []

    @property
    def current(self) -> Scene | None:
        return self._stack[-1] if self._stack else None

    def push(self, scene: Scene) -> None:
        scene.game = self.game
        self._stack.append(scene)
        scene.on_enter()

    def pop(self) -> Scene | None:
        if self._stack:
            scene = self._stack.pop()
            scene.on_exit()
            return scene
        return None

    def replace(self, scene: Scene) -> None:
        self.pop()
        self.push(scene)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)

    def render(self) -> None:
        if self.current:
            self.current.render()

    def handle_events(self, events: list) -> None:
        if self.current:
            self.current.handle_events(events)
