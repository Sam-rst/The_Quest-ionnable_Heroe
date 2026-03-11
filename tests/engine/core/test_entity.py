"""Tests pour engine.core.entity."""

from engine.core.entity import Entity
from engine.core.component import Component


class DummyComponent(Component):
    def __init__(self, value: int = 0) -> None:
        self.value = value


class AnotherComponent(Component):
    def __init__(self, label: str = "") -> None:
        self.label = label


class TestEntity:
    def test_unique_ids(self):
        e1 = Entity()
        e2 = Entity()
        assert e1.id != e2.id

    def test_add_returns_self(self):
        e = Entity()
        result = e.add(DummyComponent())
        assert result is e

    def test_add_sets_entity_ref(self):
        e = Entity()
        dc = DummyComponent()
        e.add(dc)
        assert dc.entity is e

    def test_get_by_type(self):
        e = Entity()
        dc = DummyComponent(value=7)
        e.add(dc)
        assert e.get(DummyComponent) is dc
        assert e.get(DummyComponent).value == 7

    def test_get_returns_none_if_absent(self):
        e = Entity()
        assert e.get(DummyComponent) is None

    def test_has_single(self):
        e = Entity()
        e.add(DummyComponent())
        assert e.has(DummyComponent)

    def test_has_multiple(self):
        e = Entity()
        e.add(DummyComponent())
        e.add(AnotherComponent())
        assert e.has(DummyComponent, AnotherComponent)

    def test_has_partial_returns_false(self):
        e = Entity()
        e.add(DummyComponent())
        assert not e.has(DummyComponent, AnotherComponent)

    def test_remove(self):
        e = Entity()
        dc = DummyComponent()
        e.add(dc)
        removed = e.remove(DummyComponent)
        assert removed is dc
        assert dc.entity is None
        assert e.get(DummyComponent) is None

    def test_remove_absent_returns_none(self):
        e = Entity()
        assert e.remove(DummyComponent) is None

    def test_repr(self):
        e = Entity()
        e.add(DummyComponent())
        r = repr(e)
        assert "Entity(" in r
        assert "DummyComponent" in r
