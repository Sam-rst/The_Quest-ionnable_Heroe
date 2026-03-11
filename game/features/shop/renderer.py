"""Rendu de l'UI du marchand."""

import pygame
import sys
from game.features.shop.logic import load_shop_config, try_purchase
from game.features.inventory.components import InventoryComponent


def run_shop_menu(screen: pygame.Surface, inventory: InventoryComponent,
                  potion_image=None, font_path: str | None = None) -> None:
    """Boucle bloquante pour le menu marchand."""
    largeur_bouton = 400
    bouton_potion = pygame.Rect(
        (screen.get_width() - largeur_bouton) / 2, 700, largeur_bouton, 50
    )

    config = load_shop_config()
    trades = config.get("trades", [])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_potion.collidepoint(pygame.mouse.get_pos()):
                    try_purchase(inventory, 0)
                    return
                else:
                    return

        screen.fill((0, 0, 0))

        if font_path:
            font_grand = pygame.font.Font(font_path, 50)
        else:
            font_grand = pygame.font.Font(None, 50)
        texte = font_grand.render("Bienvenue chez le marchand", True, (255, 255, 255))
        screen.blit(texte, ((screen.get_width() - texte.get_width()) / 2, 50))

        if potion_image:
            screen.blit(potion_image, ((screen.get_width() - potion_image.get_width()) / 2, 100))

        pygame.draw.rect(screen, (255, 255, 255), bouton_potion)
        pygame.draw.rect(screen, (255, 0, 0), bouton_potion, 3)

        font = pygame.font.Font(None, 30)
        trade_text = trades[0]["display"] if trades else "Rien à vendre"
        texte_trade = font.render(trade_text, True, (0, 0, 0))
        screen.blit(texte_trade, (bouton_potion.x + 10, bouton_potion.y + 10))

        pygame.display.flip()
