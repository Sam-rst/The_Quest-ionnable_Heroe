"""WorldMapSystem: gestion des transitions entre maps, spawns."""

import json
import logging
import os
import random
from engine.core.system import System

logger = logging.getLogger(__name__)
from engine.features.physics.components import TransformComponent
from game.features.player.components import PlayerComponent
from game.features.enemy_ai.components import AIComponent
from game.features.npc.components import NPCComponent

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_maps_config() -> dict:
    with open(os.path.join(_DATA_DIR, "maps.json"), "r") as f:
        return json.load(f)


def load_spawns_config() -> dict:
    with open(os.path.join(_DATA_DIR, "spawns.json"), "r") as f:
        return json.load(f)


class WorldMapSystem(System):
    def __init__(self) -> None:
        self.maps_config = load_maps_config()
        self.current_map: str = "Overworld"
        self.tilemap_data: dict = {}  # map_name -> TilemapData
        logger.info("Maps config loaded: %s", list(self.maps_config.keys()))

    def update(self, dt: float) -> None:
        pass

    def get_bg_color(self, map_name: str | None = None) -> str:
        name = map_name or self.current_map
        config = self.maps_config.get(name, {})
        return config.get("bg_color", "#71ddee")

    def get_teleporter_defs(self, map_name: str) -> list[tuple[str, str, str]]:
        config = self.maps_config.get(map_name, {})
        return [
            (tp["name"], tp["destination"], tp["waypoint_back"])
            for tp in config.get("teleporters", [])
        ]

    def spawn_enemies_for_map(self, map_name: str, game, asset_loader, map_pixel_size: tuple) -> None:
        """Crée les entités ennemis assignées à cette map."""
        from game.features.character.factory import create_enemy
        spawns = load_spawns_config()

        for spawn_def in spawns.get("enemies", []):
            if spawn_def["map"] != map_name:
                continue
            x = random.randint(100, max(200, map_pixel_size[0] - 100))
            y = random.randint(100, max(200, map_pixel_size[1] - 100))
            entity = create_enemy(spawn_def["type"], spawn_def["name"], x, y, asset_loader)
            ai = entity.get(AIComponent)
            if ai:
                ai.current_map = map_name
            game.world.add_entity(entity)
            logger.debug("Spawned enemy %s (%s) on %s", spawn_def["name"], spawn_def["type"], map_name)

    def spawn_npcs_for_map(self, map_name: str, game, asset_loader,
                           tilemap_data=None, map_pixel_size: tuple = (2000, 2000)) -> None:
        """Crée les entités PNJ assignées à cette map."""
        from game.features.character.factory import create_npc
        spawns = load_spawns_config()

        for spawn_def in spawns.get("npcs", []):
            if spawn_def["map"] != map_name:
                continue
            npc_type = spawn_def["type"]

            # Get position from waypoint or random
            x, y = 2000.0, 1200.0
            if tilemap_data:
                # Load NPC data to check for spawn_waypoint
                char_data_dir = os.path.normpath(os.path.join(
                    os.path.dirname(__file__), "..", "character", "data"
                ))
                npcs_data_path = os.path.join(char_data_dir, "npcs.json")
                with open(npcs_data_path, "r") as f:
                    npcs_data = json.load(f)
                npc_data = npcs_data.get(npc_type, {})
                wp_name = npc_data.get("spawn_waypoint")
                if wp_name:
                    pos = tilemap_data.get_waypoint(wp_name)
                    if pos:
                        x, y = pos
                if npc_data.get("random_spawn"):
                    x = random.randint(500, max(600, map_pixel_size[0] - 500))
                    y = random.randint(500, max(600, map_pixel_size[1] - 500))

            entity = create_npc(npc_type, spawn_def["name"], x, y, asset_loader)
            npc_comp = entity.get(NPCComponent)
            if npc_comp:
                npc_comp.current_map = map_name
            game.world.add_entity(entity)
            logger.debug("Spawned NPC %s (%s) on %s", spawn_def["name"], npc_type, map_name)
