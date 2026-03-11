"""Components de physique — données pures, pas de pygame."""

from engine.core.component import Component


class TransformComponent(Component):
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = x
        self.y = y
        self.old_x = x
        self.old_y = y

    def save_old(self) -> None:
        self.old_x = self.x
        self.old_y = self.y


class VelocityComponent(Component):
    def __init__(self, dx: float = 0.0, dy: float = 0.0, speed: float = 0.0) -> None:
        self.dx = dx
        self.dy = dy
        self.speed = speed

    @property
    def magnitude(self) -> float:
        return (self.dx ** 2 + self.dy ** 2) ** 0.5

    def normalize(self) -> None:
        mag = self.magnitude
        if mag != 0:
            self.dx /= mag
            self.dy /= mag


class ColliderComponent(Component):
    def __init__(self, width: float = 0.0, height: float = 0.0,
                 offset_x: float = 0.0, offset_y: float = 0.0) -> None:
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y

    @property
    def left(self) -> float:
        if self.entity:
            transform = self.entity.get(TransformComponent)
            if transform:
                return transform.x + self.offset_x
        return self.offset_x

    @property
    def right(self) -> float:
        return self.left + self.width

    @property
    def top(self) -> float:
        if self.entity:
            transform = self.entity.get(TransformComponent)
            if transform:
                return transform.y + self.offset_y
        return self.offset_y

    @property
    def bottom(self) -> float:
        return self.top + self.height
