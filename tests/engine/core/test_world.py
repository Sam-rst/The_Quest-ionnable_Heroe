"""Tests pour engine.core.world."""

from engine.core.world import World
from engine.core.entity import Entity
from engine.core.component import Component


class DummyComponent(Component):
    def __init__(self, value: int = 0) -> None:
        self.value = value


class AnotherComponent(Component):
    def __init__(self, label: str = "") -> None:
        self.label = label


class TestWorld:
    def test_create_entity(self):
        w = World()
        e = w.create_entity()
        assert isinstance(e, Entity)

    def test_add_entity(self):
        w = World()
        e = Entity()
        w.add_entity(e)
        assert w.get_entity(e.id) is e

    def test_remove_entity(self):
        w = World()
        e = w.create_entity()
        removed = w.remove_entity(e.id)
        assert removed is e
        assert w.get_entity(e.id) is None

    def test_remove_nonexistent(self):
        w = World()
        assert w.remove_entity(9999) is None

    def test_get_entity(self):
        w = World()
        e = w.create_entity()
        assert w.get_entity(e.id) is e

    def test_query_single_type(self):
        w = World()
        e1 = w.create_entity()
        e1.add(DummyComponent())
        e2 = w.create_entity()  # no component
        result = list(w.query(DummyComponent))
        assert e1 in result
        assert e2 not in result

    def test_query_multiple_types(self):
        w = World()
        e1 = w.create_entity()
        e1.add(DummyComponent())
        e1.add(AnotherComponent())
        e2 = w.create_entity()
        e2.add(DummyComponent())
        result = list(w.query(DummyComponent, AnotherComponent))
        assert e1 in result
        assert e2 not in result

    def test_query_empty(self):
        w = World()
        w.create_entity()
        result = list(w.query(DummyComponent))
        assert result == []

    def test_query_one(self):
        w = World()
        e = w.create_entity()
        e.add(DummyComponent())
        assert w.query_one(DummyComponent) is e

    def test_query_one_returns_none(self):
        w = World()
        assert w.query_one(DummyComponent) is None

    def test_all_entities(self):
        w = World()
        e1 = w.create_entity()
        e2 = w.create_entity()
        all_e = list(w.all_entities())
        assert e1 in all_e
        assert e2 in all_e
        assert len(all_e) == 2

    def test_clear(self):
        w = World()
        w.create_entity()
        w.create_entity()
        w.clear()
        assert len(w) == 0
        assert list(w.all_entities()) == []
