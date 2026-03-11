"""PlayerSystem: lit InputState pour calculer vélocité, tir, etc."""

import logging
import math
from engine.core.system import System

logger = logging.getLogger(__name__)
from engine.features.input.logic import InputAction, InputState
from engine.features.physics.components import TransformComponent, VelocityComponent
from engine.features.sprite.components import AnimationSetComponent
from game.features.character.components import StatsComponent
from game.features.player.components import PlayerComponent


class PlayerSystem(System):
    def __init__(self, input_state: InputState) -> None:
        self.input_state = input_state

    def update(self, dt: float) -> None:
        world = self.game.world
        for entity in world.query(PlayerComponent, TransformComponent, VelocityComponent):
            player = entity.get(PlayerComponent)
            velocity = entity.get(VelocityComponent)
            anim = entity.get(AnimationSetComponent)
            stats = entity.get(StatsComponent)
            transform = entity.get(TransformComponent)

            transform.save_old()

            # Mouvement
            dx, dy = 0.0, 0.0
            moving = False

            if self.input_state.is_pressed(InputAction.MOVE_UP):
                dy = -1
                if anim:
                    anim.current_animation = "Top Walk"
                moving = True
            elif self.input_state.is_pressed(InputAction.MOVE_DOWN):
                dy = 1
                if anim:
                    anim.current_animation = "Bottom Walk"
                moving = True

            if self.input_state.is_pressed(InputAction.MOVE_RIGHT):
                dx = 1
                if anim:
                    anim.current_animation = "Right Walk"
                moving = True
            elif self.input_state.is_pressed(InputAction.MOVE_LEFT):
                dx = -1
                if anim:
                    anim.current_animation = "Left Walk"
                moving = True

            # Normalize diagonal
            mag = math.sqrt(dx * dx + dy * dy)
            if mag > 0:
                dx /= mag
                dy /= mag

            velocity.dx = dx
            velocity.dy = dy

            if anim:
                anim.is_playing = moving
                if not moving:
                    anim.frame_index = 0

            # Tir
            if stats and self.input_state.mouse_clicked:
                ticks = self.game.time.ticks
                if ticks - stats.last_shot_time > stats.cooldown:
                    self.game.event_bus.emit("player_shoot",
                                            entity=entity,
                                            mouse_pos=self.input_state.mouse_pos)
                    stats.last_shot_time = ticks
                    logger.debug("Player shoot")

            # Mort
            if stats and not stats.is_alive():
                logger.info("Player died (HP=0)")
                self.game.event_bus.emit("player_died", entity=entity)
