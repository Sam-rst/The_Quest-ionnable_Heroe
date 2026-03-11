"""PhysicsSystem: intégration de la vélocité et résolution AABB."""

from engine.core.system import System
from engine.features.physics.components import (
    TransformComponent, VelocityComponent, ColliderComponent,
)


class PhysicsSystem(System):
    def update(self, dt: float) -> None:
        world = self.game.world
        for entity in world.query(TransformComponent, VelocityComponent):
            transform = entity.get(TransformComponent)
            velocity = entity.get(VelocityComponent)
            transform.save_old()
            transform.x += velocity.dx * velocity.speed * dt
            transform.y += velocity.dy * velocity.speed * dt


def aabb_overlap(a: ColliderComponent, b: ColliderComponent) -> bool:
    return (a.left < b.right and a.right > b.left and
            a.top < b.bottom and a.bottom > b.top)
