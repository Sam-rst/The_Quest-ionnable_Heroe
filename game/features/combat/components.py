"""Projectile component."""

from engine.core.component import Component


class ProjectileComponent(Component):
    def __init__(self, owner_id: int = -1, dx: float = 0, dy: float = 0,
                 speed: float = 1000, attack_range: int = 10, damage: int = 0,
                 is_enemy: bool = False) -> None:
        self.owner_id = owner_id
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.attack_range = attack_range
        self.damage = damage
        self.distance_traveled: float = 0
        self.is_enemy = is_enemy
