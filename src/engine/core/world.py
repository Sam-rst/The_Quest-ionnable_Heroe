"""World: stocke toutes les entités et permet des queries par components."""

from __future__ import annotations
from typing import Iterator
from engine.core.entity import Entity
from engine.core.component import Component


class World:
    def __init__(self) -> None:
        self._entities: dict[int, Entity] = {}

    def create_entity(self) -> Entity:
        entity = Entity()
        self._entities[entity.id] = entity
        return entity

    def add_entity(self, entity: Entity) -> None:
        self._entities[entity.id] = entity

    def remove_entity(self, entity_id: int) -> Entity | None:
        return self._entities.pop(entity_id, None)

    def get_entity(self, entity_id: int) -> Entity | None:
        return self._entities.get(entity_id)

    def query(self, *comp_types: type) -> Iterator[Entity]:
        for entity in self._entities.values():
            if entity.has(*comp_types):
                yield entity

    def query_one(self, *comp_types: type) -> Entity | None:
        for entity in self.query(*comp_types):
            return entity
        return None

    def all_entities(self) -> Iterator[Entity]:
        yield from self._entities.values()

    def clear(self) -> None:
        self._entities.clear()

    def __len__(self) -> int:
        return len(self._entities)
