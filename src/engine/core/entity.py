"""Entity: un ID unique + un dictionnaire de components."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.core.component import Component


class Entity:
    _next_id: int = 0

    def __init__(self) -> None:
        self.id: int = Entity._next_id
        Entity._next_id += 1
        self._components: dict[type, Component] = {}

    def add(self, component: Component) -> "Entity":
        self._components[type(component)] = component
        component.entity = self
        return self

    def get(self, comp_type: type) -> Component | None:
        return self._components.get(comp_type)

    def has(self, *comp_types: type) -> bool:
        return all(ct in self._components for ct in comp_types)

    def remove(self, comp_type: type) -> Component | None:
        comp = self._components.pop(comp_type, None)
        if comp is not None:
            comp.entity = None
        return comp

    def __repr__(self) -> str:
        comps = ", ".join(c.__class__.__name__ for c in self._components.values())
        return f"Entity({self.id}, [{comps}])"
