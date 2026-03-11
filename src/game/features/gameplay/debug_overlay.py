"""DebugOverlay: affiche FPS, entités, position joueur, map courante."""

import pygame

from engine.features.physics.components import TransformComponent
from game.features.player.components import PlayerComponent


class DebugOverlay:
    def __init__(self) -> None:
        self.enabled = False
        self._clock: pygame.time.Clock | None = None
        self._font: pygame.font.Font | None = None

    def init(self, clock: pygame.time.Clock) -> None:
        self._clock = clock
        self._font = pygame.font.SysFont("monospace", 18)

    def render(self, screen: pygame.Surface, world, current_map: str) -> None:
        if not self.enabled or not self._font:
            return

        fps = self._clock.get_fps() if self._clock else 0.0
        entity_count = len(world)

        player_pos = "N/A"
        for entity in world.query(PlayerComponent, TransformComponent):
            t = entity.get(TransformComponent)
            player_pos = f"{t.x:.0f}, {t.y:.0f}"
            break

        lines = [
            f"FPS: {fps:.0f}",
            f"Entités: {entity_count}",
            f"Position: {player_pos}",
            f"Map: {current_map}",
        ]

        padding = 6
        line_h = 20
        box_w = 260
        box_h = padding * 2 + line_h * len(lines)

        overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (8, 8))

        for i, line in enumerate(lines):
            surf = self._font.render(line, True, (0, 255, 0))
            screen.blit(surf, (8 + padding, 8 + padding + i * line_h))
