"""Rendu des items au sol."""

import pygame
from engine.features.physics.components import TransformComponent
from engine.features.sprite.components import SpriteComponent
from game.features.inventory.components import DroppedItemComponent


def draw_dropped_items(surface: pygame.Surface, game, offset_x: float, offset_y: float,
                       current_map: str, item_frames: dict | None = None) -> None:
    for entity in game.world.query(DroppedItemComponent, TransformComponent):
        drop = entity.get(DroppedItemComponent)
        transform = entity.get(TransformComponent)

        if drop.current_map != current_map:
            continue

        frames = (item_frames or {}).get(drop.item_name)
        if frames:
            drop.animation_index += drop.animation_speed
            if drop.animation_index >= len(frames):
                drop.animation_index = 0
            img = frames[int(drop.animation_index)]
            w = int(img.get_width() * 4)
            h = int(img.get_height() * 4)
            img = pygame.transform.scale(img, (w, h))
            surface.blit(img, (transform.x - offset_x, transform.y - offset_y))
