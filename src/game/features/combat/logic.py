"""CombatSystem: trajectoire, impact, dégâts des projectiles."""

import logging
import math
from engine.core.system import System

logger = logging.getLogger(__name__)
from engine.core.entity import Entity
from engine.features.physics.components import TransformComponent
from engine.features.sprite.components import SpriteComponent, AnimationSetComponent
from game.features.combat.components import ProjectileComponent
from game.features.character.components import StatsComponent
from game.features.player.components import PlayerComponent
from game.features.enemy_ai.components import AIComponent


class CombatSystem(System):
    def __init__(self) -> None:
        self._pending_player_shots: list[dict] = []
        self._pending_enemy_shots: list[dict] = []

    def on_enter(self) -> None:
        self.game.event_bus.subscribe("player_shoot", self._on_player_shoot)
        self.game.event_bus.subscribe("enemy_shoot", self._on_enemy_shoot)

    def _on_player_shoot(self, entity, mouse_pos, **kw) -> None:
        self._pending_player_shots.append({"entity": entity, "mouse_pos": mouse_pos})

    def _on_enemy_shoot(self, entity, target_x, target_y, **kw) -> None:
        self._pending_enemy_shots.append({"entity": entity, "target_x": target_x, "target_y": target_y})

    def update(self, dt: float) -> None:
        world = self.game.world

        # Spawn player projectiles
        for shot in self._pending_player_shots:
            self._create_player_projectile(shot["entity"], shot["mouse_pos"])
        self._pending_player_shots.clear()

        # Spawn enemy projectiles
        for shot in self._pending_enemy_shots:
            self._create_enemy_projectile(shot["entity"], shot["target_x"], shot["target_y"])
        self._pending_enemy_shots.clear()

        # Update projectiles
        to_remove = []
        for entity in world.query(ProjectileComponent, TransformComponent):
            proj = entity.get(ProjectileComponent)
            transform = entity.get(TransformComponent)

            transform.x += proj.dx * proj.speed * dt
            transform.y += proj.dy * proj.speed * dt
            proj.distance_traveled += 1

            if proj.distance_traveled >= proj.attack_range:
                to_remove.append(entity.id)
                logger.debug("Projectile expired: entity %d", entity.id)
                continue

            # Check collisions
            if proj.is_enemy:
                # Hit player
                for player_ent in world.query(PlayerComponent, TransformComponent, StatsComponent):
                    pt = player_ent.get(TransformComponent)
                    ps = player_ent.get(StatsComponent)
                    if self._collides(transform, pt, 30):
                        ps.take_damage(proj.damage)
                        to_remove.append(entity.id)
                        logger.debug("Projectile hit player: -%d dmg (HP=%d)", proj.damage, ps.hp)
                        if not ps.is_alive():
                            self.game.event_bus.emit("player_died", entity=player_ent)
                        break
            else:
                # Hit enemies
                for enemy_ent in world.query(AIComponent, TransformComponent, StatsComponent):
                    et = enemy_ent.get(TransformComponent)
                    es = enemy_ent.get(StatsComponent)
                    if self._collides(transform, et, 30):
                        es.take_damage(proj.damage)
                        to_remove.append(entity.id)
                        logger.debug("Projectile hit enemy %d: -%d dmg (HP=%d)", enemy_ent.id, proj.damage, es.hp)
                        break

        for eid in to_remove:
            world.remove_entity(eid)

    def _collides(self, a_transform, b_transform, radius: float) -> bool:
        dx = a_transform.x - b_transform.x
        dy = a_transform.y - b_transform.y
        return (dx * dx + dy * dy) < radius * radius

    def _create_player_projectile(self, shooter, mouse_pos) -> None:
        transform = shooter.get(TransformComponent)
        stats = shooter.get(StatsComponent)
        anim = shooter.get(AnimationSetComponent)
        if not transform or not stats:
            return

        # Calculate direction toward mouse (screen center offset for center camera)
        screen_info = self.game.settings.get("screen_size", (1920, 1080))
        half_w = screen_info[0] // 2
        half_h = screen_info[1] // 2
        dx = mouse_pos[0] - half_w
        dy = mouse_pos[1] - half_h
        mag = math.sqrt(dx * dx + dy * dy)
        if mag == 0:
            return
        dx /= mag
        dy /= mag

        # Set attack animation direction
        if anim:
            anim.is_attack = True
            if abs(dx) < abs(dy):
                if dy > 0:
                    anim.current_animation = "Bottom Attack"
                else:
                    anim.current_animation = "Top Attack"
            else:
                if dx > 0:
                    anim.current_animation = "Right Attack"
                else:
                    anim.current_animation = "Left Attack"

        proj_entity = Entity()
        proj_entity.add(TransformComponent(x=transform.x, y=transform.y))
        proj_entity.add(ProjectileComponent(
            owner_id=shooter.id, dx=dx, dy=dy, speed=1000,
            attack_range=stats.attack_range, damage=stats.attack, is_enemy=False,
        ))
        proj_entity.add(SpriteComponent(sprite_id="orb_red", scale=1, visible=True))
        self.game.world.add_entity(proj_entity)
        logger.debug("Player projectile created: entity %d", proj_entity.id)

    def _create_enemy_projectile(self, shooter, target_x, target_y) -> None:
        transform = shooter.get(TransformComponent)
        stats = shooter.get(StatsComponent)
        anim = shooter.get(AnimationSetComponent)
        if not transform or not stats:
            return

        dx = target_x - transform.x
        dy = target_y - transform.y
        mag = math.sqrt(dx * dx + dy * dy)
        if mag == 0:
            dy = -1
            mag = 1
        dx /= mag
        dy /= mag

        if anim:
            anim.is_attack = True
            if abs(dx) < abs(dy):
                anim.current_animation = "Bottom Attack" if dy > 0 else "Top Attack"
            else:
                anim.current_animation = "Right Attack" if dx > 0 else "Left Attack"

        proj_entity = Entity()
        proj_entity.add(TransformComponent(x=transform.x, y=transform.y))
        proj_entity.add(ProjectileComponent(
            owner_id=shooter.id, dx=dx, dy=dy, speed=1000,
            attack_range=stats.attack_range, damage=stats.attack, is_enemy=True,
        ))
        proj_entity.add(SpriteComponent(sprite_id="orb_yellow", scale=1, visible=True))
        self.game.world.add_entity(proj_entity)
        logger.debug("Enemy projectile created: entity %d", proj_entity.id)
