"""Tests pour engine.core.event_bus."""

from engine.core.event_bus import EventBus


class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus()
        received = []
        bus.subscribe("test", lambda: received.append(True))
        bus.emit("test")
        assert received == [True]

    def test_emit_with_kwargs(self):
        bus = EventBus()
        received = {}
        bus.subscribe("test", lambda x=0, y=0: received.update(x=x, y=y))
        bus.emit("test", x=10, y=20)
        assert received == {"x": 10, "y": 20}

    def test_emit_no_listeners(self):
        bus = EventBus()
        bus.emit("nonexistent")  # should not raise

    def test_multiple_listeners(self):
        bus = EventBus()
        results = []
        bus.subscribe("test", lambda: results.append("a"))
        bus.subscribe("test", lambda: results.append("b"))
        bus.emit("test")
        assert results == ["a", "b"]

    def test_unsubscribe(self):
        bus = EventBus()
        results = []
        cb = lambda: results.append(True)
        bus.subscribe("test", cb)
        bus.unsubscribe("test", cb)
        bus.emit("test")
        assert results == []

    def test_independent_event_types(self):
        bus = EventBus()
        results = []
        bus.subscribe("a", lambda: results.append("a"))
        bus.subscribe("b", lambda: results.append("b"))
        bus.emit("a")
        assert results == ["a"]

    def test_order_preserved(self):
        bus = EventBus()
        order = []
        bus.subscribe("test", lambda: order.append(1))
        bus.subscribe("test", lambda: order.append(2))
        bus.subscribe("test", lambda: order.append(3))
        bus.emit("test")
        assert order == [1, 2, 3]
