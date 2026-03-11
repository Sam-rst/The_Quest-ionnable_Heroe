"""Inventory components."""

from engine.core.component import Component


class InventoryComponent(Component):
    def __init__(self) -> None:
        self.items: list[str] = []

    def add_item(self, item_name: str) -> None:
        self.items.append(item_name)

    def remove_item(self, item_name: str) -> bool:
        if item_name in self.items:
            self.items.remove(item_name)
            return True
        return False

    def count(self, item_name: str) -> int:
        return self.items.count(item_name)


class DroppedItemComponent(Component):
    def __init__(self, item_name: str = "Piece", current_map: str = "") -> None:
        self.item_name = item_name
        self.current_map = current_map
        self.animation_index: float = 0.0
        self.animation_speed: float = 0.2
