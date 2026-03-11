"""AI components."""

from engine.core.component import Component


class AIComponent(Component):
    def __init__(self, move_cooldown: float = 1500) -> None:
        self.move_cooldown = move_cooldown
        self.last_move_time: float = 0.0
        self.current_map: str = ""
