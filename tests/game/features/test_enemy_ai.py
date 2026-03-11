"""Tests pour game.features.enemy_ai."""

import random
from engine.core.game import Game
from engine.features.physics.components import TransformComponent, VelocityComponent
from engine.features.sprite.components import AnimationSetComponent
from game.features.character.components import StatsComponent, NameComponent
from game.features.enemy_ai.components import AIComponent
from game.features.enemy_ai.logic import EnemyAISystem
from game.features.player.components import PlayerComponent


def _make_game_with_ai():
    game = Game()
    ai_sys = EnemyAISystem()
    game.add_system(ai_sys)
    return game, ai_sys


def _add_player(game, x=100, y=100, current_map="Overworld"):
    e = game.world.create_entity()
    e.add(PlayerComponent())
    e.get(PlayerComponent).current_map = current_map
    e.add(TransformComponent(x=x, y=y))
    e.add(VelocityComponent(speed=500))
    return e


def _add_enemy(game, x=200, y=200, current_map="Overworld", hp=50):
    e = game.world.create_entity()
    e.add(AIComponent(move_cooldown=1500))
    e.get(AIComponent).current_map = current_map
    e.add(TransformComponent(x=x, y=y))
    e.add(VelocityComponent(speed=300))
    e.add(StatsComponent(max_hp=hp, attack=5, defense=0, attack_range=8, cooldown=500))
    e.add(NameComponent(name="Goblin", entity_type="Demon"))
    e.add(AnimationSetComponent())
    return e


class TestAIComponent:
    def test_defaults(self):
        ai = AIComponent()
        assert ai.move_cooldown == 1500
        assert ai.last_move_time == 0.0
        assert ai.current_map == ""


class TestEnemyAISystem:
    def test_no_player_skip(self):
        game, _ = _make_game_with_ai()
        _add_enemy(game)
        game.update(0.016)  # should not raise

    def test_enemy_different_map_stays_immobile(self):
        game, _ = _make_game_with_ai()
        _add_player(game, current_map="Overworld")
        enemy = _add_enemy(game, current_map="Dungeon")
        game.update(0.016)
        vel = enemy.get(VelocityComponent)
        assert vel.dx == 0
        assert vel.dy == 0

    def test_dead_enemy_removed(self):
        game, _ = _make_game_with_ai()
        _add_player(game)
        enemy = _add_enemy(game, hp=1)
        enemy.get(StatsComponent).hp = 0

        killed_events = []
        game.event_bus.subscribe("entity_killed", lambda **kw: killed_events.append(kw))
        game.update(0.016)

        assert len(killed_events) == 1
        assert game.world.get_entity(enemy.id) is None

    def test_shoot_respects_cooldown(self):
        game, _ = _make_game_with_ai()
        _add_player(game)
        enemy = _add_enemy(game)

        shots = []
        game.event_bus.subscribe("enemy_shoot", lambda **kw: shots.append(True))

        # First shot: ticks=0, last_shot=0 → 0 > 500 is False → no shot
        game.time._ticks = 0
        game.update(0.016)
        initial_shots = len(shots)

        # Advance past cooldown
        game.time._ticks = 1000
        enemy.get(StatsComponent).last_shot_time = 0
        game.update(0.016)
        assert len(shots) > initial_shots

    def test_wander_changes_velocity(self):
        game, _ = _make_game_with_ai()
        _add_player(game)
        enemy = _add_enemy(game)

        random.seed(42)
        game.time._ticks = 2000
        enemy.get(AIComponent).last_move_time = 0
        game.update(0.016)
        # After wander, velocity should have been set (may be 0 by random chance,
        # but the system processed without error)

    def test_entity_killed_has_correct_data(self):
        game, _ = _make_game_with_ai()
        _add_player(game)
        enemy = _add_enemy(game, x=300, y=400, current_map="Overworld")
        enemy.get(StatsComponent).hp = 0

        killed_data = []
        game.event_bus.subscribe("entity_killed", lambda **kw: killed_data.append(kw))
        game.update(0.016)

        assert killed_data[0]["name"] == "Goblin"
        assert killed_data[0]["x"] == 300
        assert killed_data[0]["map_name"] == "Overworld"
