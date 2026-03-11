"""Tests pour engine.features.scene."""

import pytest
from engine.core.game import Game
from engine.features.scene.logic import Scene, SceneManager


class DummyScene(Scene):
    def __init__(self):
        self.entered = False
        self.exited = False
        self.updated = False

    def on_enter(self):
        self.entered = True

    def on_exit(self):
        self.exited = True

    def update(self, dt):
        self.updated = True

    def render(self):
        pass


class TestScene:
    def test_scene_is_abstract(self):
        with pytest.raises(TypeError):
            Scene()


class TestSceneManager:
    def test_push_and_on_enter(self):
        game = Game()
        sm = SceneManager(game)
        scene = DummyScene()
        sm.push(scene)
        assert scene.entered

    def test_push_sets_game_ref(self):
        game = Game()
        sm = SceneManager(game)
        scene = DummyScene()
        sm.push(scene)
        assert scene.game is game

    def test_pop_and_on_exit(self):
        game = Game()
        sm = SceneManager(game)
        scene = DummyScene()
        sm.push(scene)
        popped = sm.pop()
        assert popped is scene
        assert scene.exited

    def test_pop_empty_returns_none(self):
        game = Game()
        sm = SceneManager(game)
        assert sm.pop() is None

    def test_replace(self):
        game = Game()
        sm = SceneManager(game)
        s1 = DummyScene()
        s2 = DummyScene()
        sm.push(s1)
        sm.replace(s2)
        assert s1.exited
        assert s2.entered
        assert sm.current is s2

    def test_stack_depth(self):
        game = Game()
        sm = SceneManager(game)
        sm.push(DummyScene())
        sm.push(DummyScene())
        assert len(sm._stack) == 2

    def test_current(self):
        game = Game()
        sm = SceneManager(game)
        assert sm.current is None
        s = DummyScene()
        sm.push(s)
        assert sm.current is s

    def test_update_delegates(self):
        game = Game()
        sm = SceneManager(game)
        s = DummyScene()
        sm.push(s)
        sm.update(0.016)
        assert s.updated
