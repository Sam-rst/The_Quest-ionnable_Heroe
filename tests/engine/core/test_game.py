"""Tests pour engine.core.game."""

from engine.core.game import Game
from engine.core.system import System, Feature
from engine.core.world import World
from engine.core.event_bus import EventBus
from engine.core.time_manager import TimeManager


class StubSystem(System):
    def __init__(self):
        self.update_count = 0
        self.entered = False

    def update(self, dt: float) -> None:
        self.update_count += 1

    def on_enter(self) -> None:
        self.entered = True


class StubFeature(Feature):
    def __init__(self):
        self.registered = False

    def register(self, game) -> None:
        self.registered = True


class TestGame:
    def test_has_world(self):
        g = Game()
        assert isinstance(g.world, World)

    def test_has_event_bus(self):
        g = Game()
        assert isinstance(g.event_bus, EventBus)

    def test_has_time_manager(self):
        g = Game()
        assert isinstance(g.time, TimeManager)

    def test_running_false_at_start(self):
        g = Game()
        assert g.running is False

    def test_add_system_sets_game_ref_and_calls_on_enter(self):
        g = Game()
        s = StubSystem()
        g.add_system(s)
        assert s.game is g
        assert s.entered

    def test_update_calls_all_systems(self):
        g = Game()
        s1 = StubSystem()
        s2 = StubSystem()
        g.add_system(s1)
        g.add_system(s2)
        g.update(0.016)
        assert s1.update_count == 1
        assert s2.update_count == 1

    def test_add_feature_calls_register(self):
        g = Game()
        f = StubFeature()
        g.add_feature(f)
        assert f.registered
        assert f.game is g

    def test_quit(self):
        g = Game()
        g.running = True
        g.quit()
        assert g.running is False

    def test_settings_dict(self):
        g = Game()
        assert isinstance(g.settings, dict)
        g.settings["key"] = "value"
        assert g.settings["key"] == "value"
