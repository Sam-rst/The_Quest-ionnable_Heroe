"""CharacterRenderer: dessine les barres de vie."""

import pygame
from engine.features.physics.components import TransformComponent
from engine.features.sprite.components import SpriteComponent
from game.features.character.components import StatsComponent

BAR_WIDTH = 100
BAR_HEIGHT = 10


def draw_health_bar(surface: pygame.Surface, entity, offset_x: float, offset_y: float) -> None:
    stats = entity.get(StatsComponent)
    transform = entity.get(TransformComponent)
    if not stats or not transform:
        return
    # Centrer la barre sur le sprite
    sprite = entity.get(SpriteComponent) if entity.has(SpriteComponent) else None
    if sprite and sprite._cached_scaled:
        cx = transform.x + sprite._cached_w / 2 - offset_x
    else:
        cx = transform.x - offset_x
    life_ratio = stats.hp / stats.max_hp if stats.max_hp > 0 else 0
    x = cx - BAR_WIDTH / 2
    y = transform.y - 10 - offset_y
    pygame.draw.rect(surface, '#ff0000', pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT), 5)
    pygame.draw.rect(surface, '#00ff00', pygame.Rect(x, y, BAR_WIDTH * life_ratio, BAR_HEIGHT), 5)
