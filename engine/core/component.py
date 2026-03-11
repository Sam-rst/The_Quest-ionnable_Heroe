"""Component base class — pure data, no logic."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.core.entity import Entity


class Component:
    entity: Entity | None = None
