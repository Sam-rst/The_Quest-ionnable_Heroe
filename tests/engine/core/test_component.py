"""Tests pour engine.core.component."""

from engine.core.component import Component


class _Dummy(Component):
    def __init__(self, value: int = 0) -> None:
        self.value = value


class TestComponent:
    def test_entity_ref_default_none(self):
        c = Component()
        assert c.entity is None

    def test_subclassable(self):
        dc = _Dummy(value=42)
        assert isinstance(dc, Component)
        assert dc.value == 42

    def test_entity_set_by_add(self):
        from engine.core.entity import Entity
        e = Entity()
        dc = _Dummy()
        e.add(dc)
        assert dc.entity is e
