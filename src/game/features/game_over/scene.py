"""GameOverScene: affiche 'Game Over' et permet le respawn."""

import logging
import pygame
import sys
from engine.features.scene.logic import Scene

logger = logging.getLogger(__name__)


class GameOverScene(Scene):
    def __init__(self, save_manager) -> None:
        self.save_manager = save_manager
        self.screen: pygame.Surface | None = None
        self.respawned = False

    def on_enter(self) -> None:
        logger.info("Game Over affiché")
        self.screen = pygame.display.get_surface()
        self.respawned = False

    def handle_events(self, events: list) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key in (pygame.K_e, pygame.K_SPACE):
                    logger.info("Respawn demandé")
                    self.save_manager.delete()
                    self.respawned = True

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        if not self.screen:
            return
        self.screen.fill('#000000')
        font = pygame.font.SysFont(None, 64)
        text_surf = font.render("Game Over appuyez sur SPACE pour respawn", True, (255, 0, 0))
        text_rect = text_surf.get_rect(center=(
            self.screen.get_size()[0] // 2,
            self.screen.get_size()[1] // 2
        ))
        self.screen.blit(text_surf, text_rect)
        pygame.display.update()
