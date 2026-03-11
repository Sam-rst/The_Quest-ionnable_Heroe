"""Tests pour engine.features.ui."""

from engine.features.ui.logic import UIElement
from engine.features.ui.widgets import Button, Label, ProgressBar


class TestUIElement:
    def test_defaults(self):
        el = UIElement()
        assert el.name == ""
        assert el.x == 0
        assert el.visible is True

    def test_contains_point_inside(self):
        el = UIElement(name="btn", x=10, y=10, width=100, height=50)
        assert el.contains_point(50, 30)

    def test_contains_point_outside(self):
        el = UIElement(name="btn", x=10, y=10, width=100, height=50)
        assert not el.contains_point(200, 200)

    def test_contains_point_edge(self):
        el = UIElement(name="btn", x=10, y=10, width=100, height=50)
        assert el.contains_point(10, 10)
        assert el.contains_point(110, 60)

    def test_children(self):
        parent = UIElement(name="parent")
        child = UIElement(name="child")
        parent.children.append(child)
        assert len(parent.children) == 1
        assert parent.children[0] is child


class TestButton:
    def test_creation_and_inheritance(self):
        b = Button("ok", 10, 20, 100, 50, label="OK")
        assert isinstance(b, UIElement)
        assert b.label == "OK"
        assert b.name == "ok"


class TestLabel:
    def test_creation_and_inheritance(self):
        lb = Label("title", 0, 0, text="Hello")
        assert isinstance(lb, UIElement)
        assert lb.text == "Hello"


class TestProgressBar:
    def test_creation_and_inheritance(self):
        pb = ProgressBar("hp", 0, 0, 200, 20, value=0.75)
        assert isinstance(pb, UIElement)
        assert pb.value == 0.75
