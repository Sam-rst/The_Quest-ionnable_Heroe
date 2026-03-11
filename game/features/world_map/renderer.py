"""WorldMap renderer: couleur de fond par map."""

import pygame


def fill_background(surface: pygame.Surface, bg_color: str) -> None:
    surface.fill(bg_color)
