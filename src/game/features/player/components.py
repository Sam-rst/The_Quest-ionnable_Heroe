"""Player component."""

from engine.core.component import Component


class PlayerComponent(Component):
    def __init__(self) -> None:
        self.is_teleporting: bool = False
        self.current_map: str = "Overworld"
