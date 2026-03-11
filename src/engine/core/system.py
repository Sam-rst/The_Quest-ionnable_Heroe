"""System et Feature: classes de base pour la logique de jeu."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.core.game import Game


class System(ABC):
    """Un système traite les entités à chaque frame."""

    game: Game | None = None

    @abstractmethod
    def update(self, dt: float) -> None: ...

    def on_enter(self) -> None:
        """Appelé quand le système est ajouté au jeu."""

    def on_exit(self) -> None:
        """Appelé quand le système est retiré."""


class Feature(ABC):
    """Une feature regroupe un ou plusieurs systèmes et s'enregistre dans le Game."""

    game: Game | None = None

    @abstractmethod
    def register(self, game: Game) -> None:
        """Enregistrer les systèmes, les event listeners, etc."""

    def unregister(self) -> None:
        """Nettoyage en cas de suppression."""
