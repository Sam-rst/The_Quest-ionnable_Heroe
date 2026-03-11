"""NPC components."""

from engine.core.component import Component


class NPCComponent(Component):
    def __init__(self, npc_type: str = "", interactable: bool = False,
                 wanders: bool = False, move_cooldown: float = 1500) -> None:
        self.npc_type = npc_type
        self.interactable = interactable
        self.wanders = wanders
        self.move_cooldown = move_cooldown
        self.last_move_time: float = 0.0
        self.current_map: str = ""
