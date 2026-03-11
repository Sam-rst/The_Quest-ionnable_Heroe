"""MainMenuScene: sélection de classe ou chargement de sauvegarde."""

import logging
import pygame
import sys
from engine.features.scene.logic import Scene

logger = logging.getLogger(__name__)


CLASS_LIST = ["Warrior", "Mage", "Assassin", "Guard", "Archer", "Tank"]
CLASS_DISPLAY = ["Guerrier", "Mage", "Assassin", "Garde", "Archer", "Tank"]


class MainMenuScene(Scene):
    def __init__(self, save_manager, asset_loader, font_path: str | None = None) -> None:
        self.save_manager = save_manager
        self.asset_loader = asset_loader
        self.font_path = font_path
        self.selected_class: str | None = None
        self.buttons: list[pygame.Rect] = []
        self.screen: pygame.Surface | None = None
        self.done = False

    def on_enter(self) -> None:
        self.screen = pygame.display.get_surface()
        # Check for existing save
        player_class = self.save_manager.get("player_class")
        if player_class:
            self.selected_class = player_class.get("Class") if isinstance(player_class, dict) else None
            if self.selected_class:
                self.done = True
                return

        # Create buttons for class selection
        largeur = 200
        self.buttons = []
        for i in range(6):
            rect = pygame.Rect(
                (self.screen.get_width() - largeur) / 2,
                300 + i * 100,
                largeur, 50
            )
            self.buttons.append(rect)

    def handle_events(self, events: list) -> None:
        if self.done:
            return
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, btn in enumerate(self.buttons):
                    if btn.collidepoint(pos):
                        self.selected_class = CLASS_LIST[i]
                        logger.info("Classe sélectionnée: %s", self.selected_class)
                        self.done = True
                        return

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        if self.done or not self.screen:
            return

        self.screen.fill((0, 0, 0))

        if self.font_path:
            font_grand = pygame.font.Font(self.font_path, 50)
            font = pygame.font.Font(self.font_path, 30)
        else:
            font_grand = pygame.font.Font(None, 50)
            font = pygame.font.Font(None, 30)

        titre1 = font_grand.render("Bienvenue dans The Quest-ionable Heroe", True, (255, 255, 255))
        titre2 = font_grand.render("Choisissez votre classe", True, (255, 255, 255))
        self.screen.blit(titre1, ((self.screen.get_width() - titre1.get_width()) / 2, 50))
        self.screen.blit(titre2, ((self.screen.get_width() - titre2.get_width()) / 2, 100))

        for i, btn in enumerate(self.buttons):
            pygame.draw.rect(self.screen, (255, 255, 255), btn)
            pygame.draw.rect(self.screen, (0, 0, 0), btn, 3)
            text = font.render(CLASS_DISPLAY[i], True, (0, 0, 0))
            self.screen.blit(text, (btn.x + 10, btn.y + 10))

        pygame.display.flip()
