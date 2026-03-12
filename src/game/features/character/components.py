"""Components pour les personnages."""

from engine.core.component import Component


class StatsComponent(Component):
    def __init__(self, max_hp: int = 1, attack: int = 1, defense: int = 1,
                 attack_range: int = 10, cooldown: int = 200, speed: float = 500) -> None:
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.attack_range = attack_range
        self.cooldown = cooldown
        self.speed = speed
        self.last_shot_time: float = 0.0
        # Régénération progressive (potion)
        self._regen_ticks: int = 0          # nombre de ticks restants (1 tick = 1s)
        self._regen_rate: float = 0.0       # % max_hp par tick
        self._regen_timer: float = 0.0      # accumulateur temps

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def regenerate(self) -> None:
        self.hp = self.max_hp

    def start_regen(self, ticks: int, rate: float) -> None:
        """Lance une régénération progressive (ticks × rate% max_hp, 1 tick/s)."""
        self._regen_ticks += ticks
        self._regen_rate = rate
        self._regen_timer = 0.0

    def update_regen(self, dt: float) -> None:
        """Applique rate% max_hp en int toutes les secondes. Appelé chaque frame."""
        if self._regen_ticks <= 0:
            return
        self._regen_timer += dt
        while self._regen_timer >= 1.0 and self._regen_ticks > 0:
            self._regen_timer -= 1.0
            self._regen_ticks -= 1
            self.hp = min(self.max_hp, self.hp + int(self.max_hp * self._regen_rate))


class ClassComponent(Component):
    def __init__(self, class_name: str = "", display_name: str = "") -> None:
        self.class_name = class_name
        self.display_name = display_name


class NameComponent(Component):
    def __init__(self, name: str = "", entity_type: str = "") -> None:
        self.name = name
        self.entity_type = entity_type
