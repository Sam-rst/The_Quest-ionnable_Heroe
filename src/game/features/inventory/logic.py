"""InventorySystem: gestion des items au sol et ramassage."""

from engine.core.system import System
from engine.core.entity import Entity
from engine.features.physics.components import TransformComponent
from engine.features.sprite.components import SpriteComponent
from game.features.inventory.components import DroppedItemComponent, InventoryComponent
from game.features.player.components import PlayerComponent


class InventorySystem(System):
    def __init__(self) -> None:
        self._pending_drops: list[dict] = []

    def on_enter(self) -> None:
        self.game.event_bus.subscribe("entity_killed", self._on_entity_killed)

    def _on_entity_killed(self, entity, name, x, y, map_name, **kw) -> None:
        self._pending_drops.append({"x": x, "y": y, "map": map_name})

    def update(self, dt: float) -> None:
        world = self.game.world

        # Create dropped items
        for drop in self._pending_drops:
            item_entity = Entity()
            item_entity.add(TransformComponent(x=drop["x"], y=drop["y"]))
            item_entity.add(DroppedItemComponent(item_name="Piece", current_map=drop["map"]))
            item_entity.add(SpriteComponent(sprite_id="piece", scale=4, visible=True))
            world.add_entity(item_entity)
        self._pending_drops.clear()
