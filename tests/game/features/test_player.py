"""Tests pour game.features.player."""

from engine.core.game import Game
from engine.features.input.logic import InputAction, InputState
from engine.features.physics.components import TransformComponent, VelocityComponent
from engine.features.sprite.components import AnimationSetComponent
from game.features.character.components import StatsComponent
from game.features.player.components import PlayerComponent
from game.features.player.logic import PlayerSystem


def _make_game_with_player(input_state):
    game = Game()
    ps = PlayerSystem(input_state)
    game.add_system(ps)

    e = game.world.create_entity()
    e.add(PlayerComponent())
    e.add(TransformComponent(x=100, y=100))
    e.add(VelocityComponent(speed=500))
    e.add(StatsComponent(max_hp=100, attack=10, defense=5, attack_range=10, cooldown=200))
    e.add(AnimationSetComponent())
    return game, e


class TestPlayerComponent:
    def test_defaults(self):
        p = PlayerComponent()
        assert p.is_teleporting is False
        assert p.current_map == "Overworld"


class TestPlayerSystem:
    def test_move_up(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        inp.press(InputAction.MOVE_UP)
        game.update(0.016)
        vel = player.get(VelocityComponent)
        assert vel.dy == -1

    def test_move_down(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        inp.press(InputAction.MOVE_DOWN)
        game.update(0.016)
        vel = player.get(VelocityComponent)
        assert vel.dy == 1

    def test_move_left(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        inp.press(InputAction.MOVE_LEFT)
        game.update(0.016)
        vel = player.get(VelocityComponent)
        assert vel.dx == -1

    def test_move_right(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        inp.press(InputAction.MOVE_RIGHT)
        game.update(0.016)
        vel = player.get(VelocityComponent)
        assert vel.dx == 1

    def test_diagonal_normalized(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        inp.press(InputAction.MOVE_UP)
        inp.press(InputAction.MOVE_RIGHT)
        game.update(0.016)
        vel = player.get(VelocityComponent)
        mag = (vel.dx ** 2 + vel.dy ** 2) ** 0.5
        assert abs(mag - 1.0) < 1e-6

    def test_no_movement_zero_velocity(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        game.update(0.016)
        vel = player.get(VelocityComponent)
        assert vel.dx == 0
        assert vel.dy == 0

    def test_animation_playing_when_moving(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        inp.press(InputAction.MOVE_UP)
        game.update(0.016)
        anim = player.get(AnimationSetComponent)
        assert anim.is_playing

    def test_shoot_emits_event(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        shots = []
        game.event_bus.subscribe("player_shoot", lambda **kw: shots.append(True))

        # Set time to allow shooting
        game.time._ticks = 1000
        player.get(StatsComponent).last_shot_time = 0

        inp.set_mouse((400, 300), True)
        game.update(0.016)
        assert len(shots) == 1

    def test_shoot_respects_cooldown(self):
        inp = InputState()
        game, player = _make_game_with_player(inp)
        shots = []
        game.event_bus.subscribe("player_shoot", lambda **kw: shots.append(True))

        game.time._ticks = 1000
        player.get(StatsComponent).last_shot_time = 900  # 100ms ago, cooldown=200

        inp.set_mouse((400, 300), True)
        game.update(0.016)
        assert len(shots) == 0
