"""Tests pour game.features.inventory."""

from engine.core.entity import Entity
from engine.core.game import Game
from engine.features.physics.components import TransformComponent
from engine.features.sprite.components import SpriteComponent
from game.features.inventory.components import InventoryComponent, DroppedItemComponent
from game.features.inventory.logic import InventorySystem


class TestInventoryComponent:
    def test_empty_by_default(self):
        inv = InventoryComponent()
        assert inv.items == []

    def test_add_item(self):
        inv = InventoryComponent()
        inv.add_item("Sword")
        assert "Sword" in inv.items

    def test_add_multiple(self):
        inv = InventoryComponent()
        inv.add_item("Piece")
        inv.add_item("Piece")
        inv.add_item("Potion")
        assert len(inv.items) == 3

    def test_remove_present(self):
        inv = InventoryComponent()
        inv.add_item("Sword")
        assert inv.remove_item("Sword") is True
        assert "Sword" not in inv.items

    def test_remove_absent(self):
        inv = InventoryComponent()
        assert inv.remove_item("Ghost") is False

    def test_count(self):
        inv = InventoryComponent()
        inv.add_item("Piece")
        inv.add_item("Piece")
        inv.add_item("Potion")
        assert inv.count("Piece") == 2

    def test_count_absent(self):
        inv = InventoryComponent()
        assert inv.count("Nothing") == 0


class TestDroppedItemComponent:
    def test_defaults(self):
        d = DroppedItemComponent()
        assert d.item_name == "Piece"
        assert d.current_map == ""


class TestInventorySystem:
    def test_entity_killed_creates_drop(self):
        game = Game()
        inv_sys = InventorySystem()
        game.add_system(inv_sys)

        game.event_bus.emit("entity_killed", entity=None, name="Goblin",
                            x=100, y=200, map_name="Overworld")
        game.update(0.016)

        drops = list(game.world.query(DroppedItemComponent))
        assert len(drops) == 1

    def test_drop_correct_position_and_map(self):
        game = Game()
        inv_sys = InventorySystem()
        game.add_system(inv_sys)

        game.event_bus.emit("entity_killed", entity=None, name="Demon",
                            x=300, y=400, map_name="Dungeon")
        game.update(0.016)

        drop = list(game.world.query(DroppedItemComponent))[0]
        transform = drop.get(TransformComponent)
        dropped = drop.get(DroppedItemComponent)
        assert transform.x == 300
        assert transform.y == 400
        assert dropped.current_map == "Dungeon"
