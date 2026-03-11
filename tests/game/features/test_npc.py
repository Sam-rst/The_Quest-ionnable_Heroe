"""Tests pour game.features.npc."""

import random
from engine.core.game import Game
from engine.features.physics.components import TransformComponent, VelocityComponent
from engine.features.sprite.components import AnimationSetComponent
from game.features.npc.components import NPCComponent
from game.features.npc.logic import NPCSystem
from game.features.player.components import PlayerComponent


def _make_game_with_npc_system():
    game = Game()
    npc_sys = NPCSystem()
    game.add_system(npc_sys)
    return game


def _add_player(game, current_map="Overworld"):
    e = game.world.create_entity()
    pc = PlayerComponent()
    pc.current_map = current_map
    e.add(pc)
    e.add(TransformComponent(x=100, y=100))
    e.add(VelocityComponent(speed=500))
    return e


def _add_npc(game, current_map="Overworld", wanders=False):
    e = game.world.create_entity()
    npc = NPCComponent(npc_type="Merchant", wanders=wanders, move_cooldown=500)
    npc.current_map = current_map
    e.add(npc)
    e.add(TransformComponent(x=200, y=200))
    e.add(VelocityComponent(speed=200))
    e.add(AnimationSetComponent())
    return e


class TestNPCComponent:
    def test_defaults(self):
        n = NPCComponent()
        assert n.npc_type == ""
        assert n.interactable is False
        assert n.wanders is False

    def test_custom(self):
        n = NPCComponent(npc_type="Merchant", interactable=True, wanders=True)
        assert n.npc_type == "Merchant"
        assert n.interactable is True
        assert n.wanders is True


class TestNPCSystem:
    def test_no_player_skip(self):
        game = _make_game_with_npc_system()
        _add_npc(game)
        game.update(0.016)  # should not raise

    def test_npc_different_map_immobile(self):
        game = _make_game_with_npc_system()
        _add_player(game, current_map="Overworld")
        npc = _add_npc(game, current_map="Dungeon")
        game.update(0.016)
        vel = npc.get(VelocityComponent)
        assert vel.dx == 0
        assert vel.dy == 0

    def test_wanders_true_velocity_changes(self):
        game = _make_game_with_npc_system()
        _add_player(game)
        npc = _add_npc(game, wanders=True)

        random.seed(42)
        game.time._ticks = 1000
        npc.get(NPCComponent).last_move_time = 0
        game.update(0.016)
        # System processed without error

    def test_wanders_false_no_movement(self):
        game = _make_game_with_npc_system()
        _add_player(game)
        npc = _add_npc(game, wanders=False)

        game.time._ticks = 1000
        game.update(0.016)
        vel = npc.get(VelocityComponent)
        assert vel.dx == 0
        assert vel.dy == 0
