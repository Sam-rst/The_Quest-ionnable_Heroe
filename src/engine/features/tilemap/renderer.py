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
            return
        self.tile_width = self.tmx.tilewidth * scale
        self.tile_height = self.tmx.tileheight * scale
        self._layers = [
            layer for layer in self.tmx.visible_layers
            if isinstance(layer, pytmx.TiledTileLayer)
        ]

    def draw(self, surface: pygame.Surface, offset_x: float, offset_y: float,
             exclude_layers: list[str] | None = None) -> None:
        if self.tmx is None:
            return
        exclude = exclude_layers or []
        for layer in self._layers:
            if layer.name in exclude:
                continue
            for x, y, image in layer.tiles():
                image = pygame.transform.scale(image, (self.tile_width, self.tile_height))
                surface.blit(image, (x * self.tile_width - offset_x,
                                     y * self.tile_height - offset_y))
