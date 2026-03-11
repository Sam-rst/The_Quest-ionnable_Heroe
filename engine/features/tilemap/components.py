"""Components pour la tilemap."""

from engine.core.component import Component


class TeleporterComponent(Component):
    def __init__(self, name: str, destination_map: str, destination_waypoint: str,
                 x: float = 0, y: float = 0, width: float = 0, height: float = 0) -> None:
        self.name = name
        self.destination_map = destination_map
        self.destination_waypoint = destination_waypoint
        self.x = x
        self.y = y
        self.width = width
        self.height = height
