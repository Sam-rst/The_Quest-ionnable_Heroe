"""Tilemap renderer: dessine les tile layers avec pygame."""

import pygame
import pytmx
from pytmx.util_pygame import load_pygame


class TilemapRenderer:
    def __init__(self, tmx_path: str, scale: int = 4) -> None:
        self.tmx = load_pygame(tmx_path)
        self.scale = scale
        self.tile_width = self.tmx.tilewidth * scale
        self.tile_height = self.tmx.tileheight * scale
        self._layers = [
            layer for layer in self.tmx.visible_layers
            if isinstance(layer, pytmx.TiledTileLayer)
        ]

    def draw(self, surface: pygame.Surface, offset_x: float, offset_y: float,
             exclude_layers: list[str] | None = None) -> None:
        exclude = exclude_layers or []
        for layer in self._layers:
            if layer.name in exclude:
                continue
            for x, y, image in layer.tiles():
                image = pygame.transform.scale(image, (self.tile_width, self.tile_height))
                surface.blit(image, (x * self.tile_width - offset_x,
                                     y * self.tile_height - offset_y))
