"""Tilemap renderer: dessine les tile layers avec pygame."""

import logging
import pygame
import pytmx
from pytmx.util_pygame import load_pygame

logger = logging.getLogger(__name__)


class TilemapRenderer:
    def __init__(self, tmx_path: str, scale: int = 4) -> None:
        self.scale = scale
        try:
            self.tmx = load_pygame(tmx_path)
        except Exception:
            logger.exception("Impossible de charger le TMX pour le rendu: %s", tmx_path)
            self.tmx = None
            self.tile_width = 16 * scale
            self.tile_height = 16 * scale
            self._layers = []
            self._tile_cache: dict[int, pygame.Surface] = {}
            return
        self.tile_width = self.tmx.tilewidth * scale
        self.tile_height = self.tmx.tileheight * scale
        self._layers = [
            layer for layer in self.tmx.visible_layers
            if isinstance(layer, pytmx.TiledTileLayer)
        ]
        # Cache: gid → surface scalée (pré-calculé une seule fois)
        self._tile_cache: dict[int, pygame.Surface] = {}
        self._prebake_tiles()

    def _prebake_tiles(self) -> None:
        """Pré-scale chaque tuile unique une seule fois."""
        for layer in self._layers:
            for x, y, image in layer.tiles():
                gid = layer.data[y][x]
                if gid not in self._tile_cache:
                    scaled = pygame.transform.scale(
                        image, (self.tile_width, self.tile_height)
                    )
                    self._tile_cache[gid] = scaled.convert_alpha()
        logger.info("Prebaked %d unique tiles", len(self._tile_cache))

    def draw(self, surface: pygame.Surface, offset_x: float, offset_y: float,
             exclude_layers: list[str] | None = None) -> None:
        if self.tmx is None:
            return
        exclude = exclude_layers or []
        tw = self.tile_width
        th = self.tile_height
        screen_w, screen_h = surface.get_size()

        # Calculer la plage de tuiles visibles
        ox = int(offset_x)
        oy = int(offset_y)
        col_start = max(0, ox // tw)
        col_end = min(self.tmx.width, (ox + screen_w) // tw + 1)
        row_start = max(0, oy // th)
        row_end = min(self.tmx.height, (oy + screen_h) // th + 1)

        cache = self._tile_cache
        blit = surface.blit

        for layer in self._layers:
            if layer.name in exclude:
                continue
            data = layer.data
            for y in range(row_start, row_end):
                row = data[y]
                py = y * th - oy
                for x in range(col_start, col_end):
                    gid = row[x]
                    tile = cache.get(gid)
                    if tile:
                        blit(tile, (x * tw - ox, py))
