"""NPCSystem: errance et interaction."""

import random
import math
from engine.core.system import System
from engine.features.physics.components import TransformComponent, VelocityComponent
from engine.features.sprite.components import AnimationSetComponent
from game.features.npc.components import NPCComponent
from game.features.player.components import PlayerComponent


class NPCSystem(System):
    def update(self, dt: float) -> None:
        world = self.game.world
        ticks = self.game.time.ticks

        player_entity = world.query_one(PlayerComponent)
        if not player_entity:
            return
        player_map = player_entity.get(PlayerComponent).current_map

        for entity in world.query(NPCComponent, TransformComponent, VelocityComponent):
            npc = entity.get(NPCComponent)
            velocity = entity.get(VelocityComponent)
            anim = entity.get(AnimationSetComponent)
            transform = entity.get(TransformComponent)

            if npc.current_map != player_map:
                velocity.dx = 0
                velocity.dy = 0
                continue

            transform.save_old()

            if npc.wanders and ticks - npc.last_move_time > npc.move_cooldown:
                if random.randint(0, 1):
                    velocity.dx = random.randint(-1, 1)
                    velocity.dy = random.randint(-1, 1)
                    if anim:
                        anim.is_playing = True
                        if velocity.dx == -1:
                            anim.current_animation = "Left Walk"
                        elif velocity.dx == 1:
                            anim.current_animation = "Right Walk"
                        if velocity.dy == -1:
                            anim.current_animation = "Top Walk"
                        elif velocity.dy == 1:
                            anim.current_animation = "Bottom Walk"
                else:
                    velocity.dx = 0
                    velocity.dy = 0
                    if anim:
                        anim.is_playing = False
                npc.last_move_time = ticks

            mag = math.sqrt(velocity.dx ** 2 + velocity.dy ** 2)
            if mag > 0:
                velocity.dx /= mag
                velocity.dy /= mag
