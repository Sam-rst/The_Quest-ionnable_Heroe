"""Tilemap logic: parse TMX vers des données pures (rects, waypoints)."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TileRect:
    x: float
    y: float
    width: float
    height: float


@dataclass
class Waypoint:
    name: str
    x: float
    y: float


@dataclass
class TeleporterData:
    name: str
    destination_map: str
    destination_waypoint: str
    x: float
    y: float
    width: float
    height: float


@dataclass
class TilemapData:
    """Données pures extraites d'un TMX — pas de pygame ici."""
    name: str
    width_tiles: int
    height_tiles: int
    tile_width: int
    tile_height: int
    scale: int = 4
    collision_rects: list[TileRect] = field(default_factory=list)
    waypoints: list[Waypoint] = field(default_factory=list)
    teleporters: list[TeleporterData] = field(default_factory=list)

    @property
    def pixel_width(self) -> int:
        return self.width_tiles * self.tile_width * self.scale

    @property
    def pixel_height(self) -> int:
        return self.height_tiles * self.tile_height * self.scale

    @property
    def scaled_tile_width(self) -> int:
        return self.tile_width * self.scale

    @property
    def scaled_tile_height(self) -> int:
        return self.tile_height * self.scale

    def get_waypoint(self, name: str) -> tuple[int, int] | None:
        for wp in self.waypoints:
            return_val = (int(wp.x * self.scale), int(wp.y * self.scale))
            if wp.name == name:
                return return_val
        return None


def parse_tmx(tmx_path: str, scale: int = 4,
              collision_layers: list[str] | None = None,
              teleporter_defs: list[tuple[str, str, str]] | None = None) -> TilemapData:
    """Parse un fichier TMX avec pytmx et retourne des données pures."""
    import pytmx
    from pytmx.util_pygame import load_pygame

    tmx = load_pygame(tmx_path)

    data = TilemapData(
        name=tmx_path.rsplit("/", 1)[-1].replace(".tmx", ""),
        width_tiles=tmx.width,
        height_tiles=tmx.height,
        tile_width=tmx.tilewidth,
        tile_height=tmx.tileheight,
        scale=scale,
    )

    # Extraire les waypoints
    for obj_group in tmx.objectgroups:
        if obj_group.name == "Waypoints":
            for obj in obj_group:
                data.waypoints.append(Waypoint(name=obj.name, x=obj.x, y=obj.y))

    # Extraire les collision rects
    collision_layers = collision_layers or ["Collisions"]
    for layer in tmx.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer) and layer.name in collision_layers:
            tw = tmx.tilewidth * scale
            th = tmx.tileheight * scale
            for x, y, _image in layer.tiles():
                data.collision_rects.append(TileRect(x * tw, y * th, tw, th))

    # Extraire les teleporters
    if teleporter_defs:
        for tp_name, dest_map, dest_wp in teleporter_defs:
            wp = None
            for obj_group in tmx.objectgroups:
                if obj_group.name == "Waypoints":
                    for obj in obj_group:
                        if obj.name == tp_name:
                            wp = obj
                            break
            if wp:
                data.teleporters.append(TeleporterData(
                    name=tp_name,
                    destination_map=dest_map,
                    destination_waypoint=dest_wp,
                    x=wp.x * scale,
                    y=wp.y * scale,
                    width=wp.width * scale if wp.width else 16 * scale,
                    height=wp.height * scale if wp.height else 16 * scale,
                ))

    return data
