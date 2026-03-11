"""Application: crée le Game, enregistre les features, lance la boucle."""

import pygame
import sys

from engine.core.game import Game
from engine.features.input.logic import InputAction, InputMap
from engine.features.input.pygame_adapter import PygameInputAdapter
from engine.features.scene.logic import SceneManager
from engine.features.save.logic import SaveManager
from engine.features.save.json_backend import JsonBackend
from engine.features.sprite.asset_loader import AssetLoader

from game import settings
from game.features.main_menu.scene import MainMenuScene
from game.features.game_over.scene import GameOverScene
from game.features.gameplay.scene import GameplayScene


def create_game() -> None:
    """Point d'entrée principal: initialise pygame et lance le jeu."""
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()

    # Core
    game = Game()

    # Save
    backend = JsonBackend(settings.SAVE_PATH)
    save_manager = SaveManager(backend)

    # Assets
    asset_loader = AssetLoader(settings.MANIFEST_PATH, assets_root=settings.ASSETS_ROOT)

    # Input mapping (ZQSD — clavier AZERTY)
    input_map = InputMap()
    input_map.bind(pygame.K_z, InputAction.MOVE_UP)
    input_map.bind(pygame.K_s, InputAction.MOVE_DOWN)
    input_map.bind(pygame.K_q, InputAction.MOVE_LEFT)
    input_map.bind(pygame.K_d, InputAction.MOVE_RIGHT)
    input_map.bind(pygame.K_e, InputAction.INTERACT)
    input_map.bind(pygame.K_a, InputAction.PICKUP)
    input_map.bind(pygame.K_r, InputAction.OPEN_SHOP)
    input_map.bind(pygame.K_1, InputAction.USE_POTION)
    input_map.bind(pygame.K_ESCAPE, InputAction.ESCAPE)
    input_map.bind(pygame.K_SPACE, InputAction.CONFIRM)

    input_adapter = PygameInputAdapter(input_map)

    # Font path
    font_path = "graphics/font/Enchanted_Land.otf"

    # Scene manager
    scene_manager = SceneManager(game)

    # --- Main Menu ---
    menu_scene = MainMenuScene(save_manager, asset_loader, font_path)
    scene_manager.push(menu_scene)

    # Run menu until class is selected
    while not menu_scene.done:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        menu_scene.handle_events(events)
        menu_scene.render()
        clock.tick(settings.FPS)

    scene_manager.pop()

    # --- Gameplay ---
    selected_class = menu_scene.selected_class
    if not selected_class:
        pygame.quit()
        sys.exit()

    # Save initial class selection
    if not save_manager.get("player_class"):
        save_manager.set("player_class", {"Class": selected_class, "Name": settings.PLAYER_NAME,
                                           "Max HP": 100, "Attack value": 10,
                                           "Defend value": 5, "Attack range": 3})
        save_manager.save()

    gameplay_scene = GameplayScene(selected_class, save_manager, asset_loader,
                                   input_adapter.state)
    scene_manager.push(gameplay_scene)

    game_over_scene = GameOverScene(save_manager)

    # --- Main Loop ---
    game.running = True
    while game.running:
        dt = game.time.tick()
        events = pygame.event.get()

        # Check quit
        for event in events:
            if event.type == pygame.QUIT:
                gameplay_scene._save_and_quit()

        # Process input
        input_adapter.process_events(events)

        current = scene_manager.current
        if current is gameplay_scene:
            gameplay_scene.handle_events(events)

            if gameplay_scene.game_over:
                scene_manager.replace(game_over_scene)
            else:
                gameplay_scene.update(dt)
                gameplay_scene.render()

        elif current is game_over_scene:
            game_over_scene.handle_events(events)
            game_over_scene.render()

            if game_over_scene.respawned:
                # Restart with a fresh menu
                scene_manager.pop()
                game.world.clear()

                menu_scene = MainMenuScene(save_manager, asset_loader, font_path)
                scene_manager.push(menu_scene)

                while not menu_scene.done:
                    events = pygame.event.get()
                    for event in events:
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    menu_scene.handle_events(events)
                    menu_scene.render()
                    clock.tick(settings.FPS)

                scene_manager.pop()
                selected_class = menu_scene.selected_class
                if not selected_class:
                    pygame.quit()
                    sys.exit()

                save_manager.reload()
                gameplay_scene = GameplayScene(selected_class, save_manager, asset_loader,
                                               input_adapter.state)
                scene_manager.push(gameplay_scene)

        pygame.display.update()
        clock.tick(settings.FPS)

    pygame.quit()
