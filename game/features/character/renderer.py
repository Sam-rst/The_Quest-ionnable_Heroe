"""CharacterRenderer: dessine les barres de vie."""

import pygame
from engine.features.physics.components import TransformComponent
from game.features.character.components import StatsComponent


def draw_health_bar(surface: pygame.Surface, entity, offset_x: float, offset_y: float) -> None:
    stats = entity.get(StatsComponent)
    transform = entity.get(TransformComponent)
    if not stats or not transform:
        return
    life_ratio = stats.hp / stats.max_hp if stats.max_hp > 0 else 0
    x = transform.x - 10 - offset_x
    y = transform.y - 10 - offset_y
    pygame.draw.rect(surface, '#ff0000', pygame.Rect(x, y, 100, 10), 5)
    pygame.draw.rect(surface, '#00ff00', pygame.Rect(x, y, 100 * life_ratio, 10), 5)
