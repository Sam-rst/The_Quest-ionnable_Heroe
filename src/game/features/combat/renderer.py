"""Rendu des projectiles."""

import pygame
from engine.features.physics.components import TransformComponent
from engine.features.sprite.components import SpriteComponent
from game.features.combat.components import ProjectileComponent


def draw_projectiles(surface: pygame.Surface, game, offset_x: float, offset_y: float,
                     orb_red_img=None, orb_yellow_img=None) -> None:
    for entity in game.world.query(ProjectileComponent, TransformComponent):
        proj = entity.get(ProjectileComponent)
        transform = entity.get(TransformComponent)
        sprite = entity.get(SpriteComponent)

        img = None
        if sprite and sprite.image:
            img = sprite.image
        elif not proj.is_enemy and orb_red_img:
            img = orb_red_img
        elif proj.is_enemy and orb_yellow_img:
            img = orb_yellow_img

        if img:
            surface.blit(img, (transform.x - offset_x, transform.y - offset_y))
