"""Player HUD renderer."""

import pygame
from game.features.character.components import StatsComponent
from game.features.player.components import PlayerComponent


def draw_player_hud(surface: pygame.Surface, game) -> None:
    world = game.world
    for entity in world.query(PlayerComponent, StatsComponent):
        stats = entity.get(StatsComponent)
        font = pygame.font.Font(None, 24)
        text = f"HP: {stats.hp}/{stats.max_hp}"
        text_surf = font.render(text, True, (255, 255, 255))
        surface.blit(text_surf, (10, 10))
