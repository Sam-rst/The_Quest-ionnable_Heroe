"""Tests pour engine.core.system."""

import pytest
from engine.core.system import System, Feature


class TestSystem:
    def test_system_is_abstract(self):
        with pytest.raises(TypeError):
            System()

    def test_subclass_update(self):
        class MySystem(System):
            def __init__(self):
                self.updated = False

            def update(self, dt: float) -> None:
                self.updated = True

        s = MySystem()
        s.update(0.016)
        assert s.updated

    def test_on_enter_noop(self):
        class MySystem(System):
            def update(self, dt: float) -> None:
                pass

        s = MySystem()
        s.on_enter()  # should not raise

    def test_feature_is_abstract(self):
        with pytest.raises(TypeError):
            Feature()
