"""Adapter pygame: lit les events pygame et remplit un InputState."""

import pygame
from engine.features.input.logic import InputAction, InputMap, InputState


class PygameInputAdapter:
    def __init__(self, input_map: InputMap) -> None:
        self.input_map = input_map
        self.state = InputState()

    def process_events(self, events: list) -> InputState:
        self.state.clear_frame()

        for event in events:
            if event.type == pygame.KEYDOWN:
                action = self.input_map.get_action(event.key)
                if action:
                    self.state.press(action)
            elif event.type == pygame.KEYUP:
                action = self.input_map.get_action(event.key)
                if action:
                    self.state.release(action)

        # Held keys (pour le mouvement continu)
        keys = pygame.key.get_pressed()
        for key_code, action in self.input_map._key_map.items():
            if keys[key_code]:
                self.state.press(action)
            else:
                self.state.release(action)

        # Souris
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        self.state.set_mouse(mouse_pos, mouse_buttons[0])

        return self.state
