"""AssetLoader: chargement lazy des sprites via manifest.json."""

from __future__ import annotations
import json
import logging
import os

logger = logging.getLogger(__name__)


class AssetLoader:
    def __init__(self, manifest_path: str, assets_root: str = "graphics") -> None:
        self.manifest_path = manifest_path
        self.base_dir = assets_root
        self._manifest: dict | None = None
        self._cache: dict[str, list] = {}

    @property
    def manifest(self) -> dict:
        if self._manifest is None:
            with open(self.manifest_path, "r") as f:
                self._manifest = json.load(f)
            logger.info("Manifest loaded: %s", self.manifest_path)
        return self._manifest

    def load_animation(self, sprite_id: str, action: str, direction: str) -> list:
        """Charge les frames d'une animation depuis le manifest.

        Returns une liste de pygame.Surface.
        """
        import pygame

        cache_key = f"{sprite_id}/{action}/{direction}"
        if cache_key in self._cache:
            logger.debug("Cache hit: %s", cache_key)
            return self._cache[cache_key]

        sprite_def = self.manifest.get("sprites", {}).get(sprite_id)
        if not sprite_def:
            logger.warning("Sprite manquant dans manifest: %s", sprite_id)
            return []
        logger.debug("Cache miss: %s", cache_key)

        base_path = os.path.join(self.base_dir, sprite_def["base_path"])
        anim_def = sprite_def.get("animations", {}).get(action, {}).get(direction)
        if not anim_def:
            return []

        frames = []
        for frame_file in anim_def:
            path = os.path.join(base_path, action, direction, frame_file)
            frames.append(pygame.image.load(path).convert_alpha())

        self._cache[cache_key] = frames
        return frames

    def load_all_animations(self, sprite_id: str) -> dict[str, list]:
        """Charge toutes les animations d'un sprite_id.

        Returns dict: {"Bottom Walk": [surfaces], "Left Attack": [surfaces], ...}
        """
        sprite_def = self.manifest.get("sprites", {}).get(sprite_id)
        if not sprite_def:
            return {}

        result = {}
        for action, directions in sprite_def.get("animations", {}).items():
            for direction, _frames in directions.items():
                key = f"{direction.capitalize()} {action.capitalize()}"
                # Mapping: walking/bottom → "Bottom Walk", attack/bottom → "Bottom Attack"
                if action == "walking":
                    key = f"{direction.capitalize()} Walk"
                elif action == "attack":
                    key = f"{direction.capitalize()} Attack"
                result[key] = self.load_animation(sprite_id, action, direction)

        return result

    def load_item_frames(self, item_id: str) -> list:
        """Charge les frames d'un item (ex: piece)."""
        import pygame

        cache_key = f"item/{item_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        item_def = self.manifest.get("items", {}).get(item_id)
        if not item_def:
            return []

        frames = []
        for frame_path in item_def.get("frames", []):
            path = os.path.join(self.base_dir, frame_path)
            frames.append(pygame.image.load(path).convert_alpha())

        self._cache[cache_key] = frames
        return frames

    def load_image(self, relative_path: str):
        """Charge une image unique."""
        import pygame

        cache_key = f"img/{relative_path}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        path = os.path.join(self.base_dir, relative_path)
        img = pygame.image.load(path).convert_alpha()
        self._cache[cache_key] = img
        return img
