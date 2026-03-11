"""EnemyAISystem: wander + tir vers le joueur."""

import random
import math
from engine.core.system import System
from engine.features.physics.components import TransformComponent, VelocityComponent
from engine.features.sprite.components import AnimationSetComponent
from game.features.character.components import StatsComponent, NameComponent
from game.features.enemy_ai.components import AIComponent
from game.features.player.components import PlayerComponent


class EnemyAISystem(System):
    def update(self, dt: float) -> None:
        world = self.game.world
        ticks = self.game.time.ticks

        # Find the player
        player_entity = world.query_one(PlayerComponent)
        if not player_entity:
            return

        player_transform = player_entity.get(TransformComponent)
        player_map = player_entity.get(PlayerComponent).current_map

        for entity in world.query(AIComponent, TransformComponent, VelocityComponent):
            ai = entity.get(AIComponent)
            transform = entity.get(TransformComponent)
            velocity = entity.get(VelocityComponent)
            stats = entity.get(StatsComponent)
            anim = entity.get(AnimationSetComponent)

            # Only update enemies on the same map
            if ai.current_map != player_map:
                velocity.dx = 0
                velocity.dy = 0
                continue

            # Check alive
            if stats and not stats.is_alive():
                name_comp = entity.get(NameComponent)
                enemy_name = name_comp.name if name_comp else ""
                self.game.event_bus.emit("entity_killed", entity=entity, name=enemy_name,
                                        x=transform.x, y=transform.y, map_name=ai.current_map)
                world.remove_entity(entity.id)
                continue

            transform.save_old()

            # Wander
            if ticks - ai.last_move_time > ai.move_cooldown:
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
                ai.last_move_time = ticks

            # Normalize
            mag = math.sqrt(velocity.dx ** 2 + velocity.dy ** 2)
            if mag > 0:
                velocity.dx /= mag
                velocity.dy /= mag

            # Shoot
            if stats and ticks - stats.last_shot_time > stats.cooldown:
                self.game.event_bus.emit("enemy_shoot", entity=entity,
                                        target_x=player_transform.x,
                                        target_y=player_transform.y)
                stats.last_shot_time = ticks
                if anim:
                    anim.is_attack = True
