"""Tests pour engine.features.physics."""

from engine.core.entity import Entity
from engine.core.game import Game
from engine.features.physics.components import (
    TransformComponent, VelocityComponent, ColliderComponent,
)
from engine.features.physics.logic import PhysicsSystem, aabb_overlap


class TestTransformComponent:
    def test_default_position(self):
        t = TransformComponent()
        assert t.x == 0.0
        assert t.y == 0.0

    def test_custom_position(self):
        t = TransformComponent(x=10, y=20)
        assert t.x == 10
        assert t.y == 20

    def test_save_old(self):
        t = TransformComponent(x=5, y=10)
        t.x = 15
        t.y = 25
        t.save_old()
        assert t.old_x == 15
        assert t.old_y == 25


class TestVelocityComponent:
    def test_defaults(self):
        v = VelocityComponent()
        assert v.dx == 0.0
        assert v.dy == 0.0
        assert v.speed == 0.0

    def test_magnitude_zero(self):
        v = VelocityComponent()
        assert v.magnitude == 0.0

    def test_magnitude_3_4_5(self):
        v = VelocityComponent(dx=3, dy=4)
        assert v.magnitude == 5.0

    def test_normalize(self):
        v = VelocityComponent(dx=3, dy=4)
        v.normalize()
        assert abs(v.dx - 0.6) < 1e-9
        assert abs(v.dy - 0.8) < 1e-9

    def test_normalize_zero(self):
        v = VelocityComponent(dx=0, dy=0)
        v.normalize()
        assert v.dx == 0.0
        assert v.dy == 0.0


class TestColliderComponent:
    def test_aabb_without_entity(self):
        c = ColliderComponent(width=10, height=20, offset_x=5, offset_y=5)
        assert c.left == 5
        assert c.top == 5
        assert c.right == 15
        assert c.bottom == 25

    def test_aabb_with_entity_and_transform(self):
        e = Entity()
        e.add(TransformComponent(x=100, y=200))
        c = ColliderComponent(width=10, height=20, offset_x=5, offset_y=5)
        e.add(c)
        assert c.left == 105
        assert c.top == 205
        assert c.right == 115
        assert c.bottom == 225


class TestPhysicsSystem:
    def test_update_applies_velocity(self):
        game = Game()
        e = game.world.create_entity()
        e.add(TransformComponent(x=0, y=0))
        e.add(VelocityComponent(dx=1, dy=0, speed=100))

        sys = PhysicsSystem()
        game.add_system(sys)
        game.update(1.0)

        assert e.get(TransformComponent).x == 100.0

    def test_diagonal_movement(self):
        game = Game()
        e = game.world.create_entity()
        e.add(TransformComponent(x=0, y=0))
        e.add(VelocityComponent(dx=1, dy=1, speed=100))

        sys = PhysicsSystem()
        game.add_system(sys)
        game.update(0.5)

        assert e.get(TransformComponent).x == 50.0
        assert e.get(TransformComponent).y == 50.0

    def test_ignores_entity_without_velocity(self):
        game = Game()
        e = game.world.create_entity()
        e.add(TransformComponent(x=10, y=10))

        sys = PhysicsSystem()
        game.add_system(sys)
        game.update(1.0)

        assert e.get(TransformComponent).x == 10


class TestAabbOverlap:
    def test_overlap_true(self):
        e1 = Entity()
        e1.add(TransformComponent(x=0, y=0))
        c1 = ColliderComponent(width=10, height=10)
        e1.add(c1)

        e2 = Entity()
        e2.add(TransformComponent(x=5, y=5))
        c2 = ColliderComponent(width=10, height=10)
        e2.add(c2)

        assert aabb_overlap(c1, c2)

    def test_overlap_false(self):
        e1 = Entity()
        e1.add(TransformComponent(x=0, y=0))
        c1 = ColliderComponent(width=10, height=10)
        e1.add(c1)

        e2 = Entity()
        e2.add(TransformComponent(x=100, y=100))
        c2 = ColliderComponent(width=10, height=10)
        e2.add(c2)

        assert not aabb_overlap(c1, c2)
