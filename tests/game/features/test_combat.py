"""Tests pour game.features.combat."""

from engine.core.entity import Entity
from engine.core.game import Game
from engine.features.physics.components import TransformComponent, VelocityComponent
from engine.features.sprite.components import SpriteComponent, AnimationSetComponent
from game.features.character.components import StatsComponent
from game.features.combat.components import ProjectileComponent
from game.features.combat.logic import CombatSystem
from game.features.player.components import PlayerComponent
from game.features.enemy_ai.components import AIComponent


def _make_game_with_combat():
    game = Game()
    game.settings["screen_size"] = (800, 600)
    cs = CombatSystem()
    game.add_system(cs)
    return game, cs


def _make_player(game, x=100, y=100, hp=100, attack=10):
    e = game.world.create_entity()
    e.add(PlayerComponent())
    e.add(TransformComponent(x=x, y=y))
    e.add(VelocityComponent(speed=500))
    e.add(StatsComponent(max_hp=hp, attack=attack, defense=0, attack_range=10, cooldown=200))
    e.add(AnimationSetComponent())
    e.add(SpriteComponent(sprite_id="player"))
    return e


def _make_enemy(game, x=200, y=200, hp=50, attack=5):
    e = game.world.create_entity()
    e.add(AIComponent())
    e.add(TransformComponent(x=x, y=y))
    e.add(VelocityComponent(speed=300))
    e.add(StatsComponent(max_hp=hp, attack=attack, defense=0, attack_range=8, cooldown=500))
    e.add(AnimationSetComponent())
    e.add(SpriteComponent(sprite_id="enemy"))
    return e


class TestProjectileComponent:
    def test_defaults(self):
        p = ProjectileComponent()
        assert p.owner_id == -1
        assert p.distance_traveled == 0
        assert p.is_enemy is False

    def test_custom(self):
        p = ProjectileComponent(owner_id=5, damage=20, is_enemy=True)
        assert p.owner_id == 5
        assert p.damage == 20
        assert p.is_enemy is True


class TestCombatSystem:
    def test_subscribe_events_on_enter(self):
        game, cs = _make_game_with_combat()
        # If subscribe worked, emitting should not raise
        game.event_bus.emit("player_shoot", entity=None, mouse_pos=(0, 0))
        game.event_bus.emit("enemy_shoot", entity=None, target_x=0, target_y=0)

    def test_collides_within_radius(self):
        cs = CombatSystem()
        a = TransformComponent(x=0, y=0)
        b = TransformComponent(x=10, y=10)
        assert cs._collides(a, b, 30)

    def test_collides_outside_radius(self):
        cs = CombatSystem()
        a = TransformComponent(x=0, y=0)
        b = TransformComponent(x=100, y=100)
        assert not cs._collides(a, b, 30)

    def test_collides_exact_boundary(self):
        cs = CombatSystem()
        a = TransformComponent(x=0, y=0)
        b = TransformComponent(x=30, y=0)
        # distance = 30, radius = 30 → 900 < 900 is False
        assert not cs._collides(a, b, 30)

    def test_player_shoot_creates_projectile(self):
        game, cs = _make_game_with_combat()
        player = _make_player(game)
        game.event_bus.emit("player_shoot", entity=player, mouse_pos=(800, 300))
        game.update(0.016)
        projs = list(game.world.query(ProjectileComponent))
        assert len(projs) == 1
        assert projs[0].get(ProjectileComponent).is_enemy is False

    def test_enemy_shoot_creates_projectile(self):
        game, cs = _make_game_with_combat()
        enemy = _make_enemy(game)
        game.event_bus.emit("enemy_shoot", entity=enemy, target_x=0, target_y=0)
        game.update(0.016)
        projs = list(game.world.query(ProjectileComponent))
        assert len(projs) == 1
        assert projs[0].get(ProjectileComponent).is_enemy is True

    def test_projectile_expires_at_range(self):
        game, cs = _make_game_with_combat()
        proj_entity = game.world.create_entity()
        proj_entity.add(TransformComponent(x=0, y=0))
        proj_entity.add(ProjectileComponent(dx=1, dy=0, speed=100, attack_range=2, damage=10))

        # Tick enough to exceed range
        for _ in range(5):
            game.update(0.016)

        projs = list(game.world.query(ProjectileComponent))
        assert len(projs) == 0

    def test_projectile_hits_player(self):
        game, cs = _make_game_with_combat()
        player = _make_player(game, x=100, y=100, hp=100)

        proj = game.world.create_entity()
        proj.add(TransformComponent(x=100, y=100))
        proj.add(ProjectileComponent(dx=0, dy=0, speed=0, attack_range=999, damage=25, is_enemy=True))

        game.update(0.016)
        assert player.get(StatsComponent).hp == 75

    def test_projectile_hits_enemy(self):
        game, cs = _make_game_with_combat()
        enemy = _make_enemy(game, x=50, y=50, hp=50)

        proj = game.world.create_entity()
        proj.add(TransformComponent(x=50, y=50))
        proj.add(ProjectileComponent(dx=0, dy=0, speed=0, attack_range=999, damage=15, is_enemy=False))

        game.update(0.016)
        assert enemy.get(StatsComponent).hp == 35

    def test_player_died_emitted_on_hp_zero(self):
        game, cs = _make_game_with_combat()
        player = _make_player(game, x=100, y=100, hp=10)

        died_events = []
        game.event_bus.subscribe("player_died", lambda **kw: died_events.append(True))

        proj = game.world.create_entity()
        proj.add(TransformComponent(x=100, y=100))
        proj.add(ProjectileComponent(dx=0, dy=0, speed=0, attack_range=999, damage=10, is_enemy=True))

        game.update(0.016)
        assert player.get(StatsComponent).hp == 0
        assert len(died_events) == 1
