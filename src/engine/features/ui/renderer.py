"""Rendu des widgets UI."""

import pygame
from engine.features.ui.logic import UIElement


def draw_button(surface: pygame.Surface, element: UIElement,
                text: str, font: pygame.font.Font,
                bg_color=(255, 255, 255), border_color=(0, 0, 0),
                text_color=(0, 0, 0)) -> None:
    rect = pygame.Rect(element.x, element.y, element.width, element.height)
    pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, border_color, rect, 3)
    text_surf = font.render(text, True, text_color)
    surface.blit(text_surf, (element.x + 10, element.y + 10))
