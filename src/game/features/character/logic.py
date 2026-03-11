"""CharacterSystem: combat math, régénération, level up."""

from engine.core.system import System
from game.features.character.components import StatsComponent


class CharacterSystem(System):
    def update(self, dt: float) -> None:
        pass

    def apply_damage(self, attacker_entity, target_entity) -> int:
        attacker_stats = attacker_entity.get(StatsComponent)
        target_stats = target_entity.get(StatsComponent)
        if not attacker_stats or not target_stats:
            return 0
        damage = max(0, attacker_stats.attack - target_stats.defense)
        target_stats.take_damage(damage)
        return damage
