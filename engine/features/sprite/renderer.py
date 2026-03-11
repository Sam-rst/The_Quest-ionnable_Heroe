"""SpriteRenderer: dessine les sprites triés par Y."""

import pygame
from engine.features.physics.components import TransformComponent
from engine.features.sprite.components import SpriteComponent


def render_sprites(surface: pygame.Surface, entities: list,
                   offset_x: float, offset_y: float, scale: float = 4) -> None:
    """Dessine les entités qui ont SpriteComponent + TransformComponent, triées par Y."""
    drawables = []
    for entity in entities:
        sprite_comp = entity.get(SpriteComponent)
        transform = entity.get(TransformComponent)
        if sprite_comp and transform and sprite_comp.visible and sprite_comp.image:
            drawables.append((transform.y, entity, sprite_comp, transform))

    drawables.sort(key=lambda d: d[0])

    for _y, entity, sprite_comp, transform in drawables:
        image = sprite_comp.image
        if scale != 1:
            w = int(image.get_width() * scale // 2.5)
            h = int(image.get_height() * scale // 2.5)
            image = pygame.transform.scale(image, (w, h))
        surface.blit(image, (transform.x - offset_x, transform.y - offset_y))
