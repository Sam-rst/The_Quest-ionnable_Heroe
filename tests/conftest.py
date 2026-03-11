"""Fixtures partagées pour toute la suite de tests."""

import pytest
from engine.core.component import Component
from engine.core.entity import Entity
from engine.core.world import World
from engine.core.event_bus import EventBus
from engine.core.game import Game
from engine.features.input.logic import InputState


class DummyComponent(Component):
    def __init__(self, value: int = 0) -> None:
        self.value = value


class AnotherComponent(Component):
    def __init__(self, label: str = "") -> None:
        self.label = label


@pytest.fixture
def entity():
    return Entity()


@pytest.fixture
def world():
    return World()


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def game():
    return Game()


@pytest.fixture
def input_state():
    return InputState()


@pytest.fixture
def player_entity():
    """Entité joueur minimale pour les tests game features."""
    from engine.features.physics.components import TransformComponent, VelocityComponent
    from game.features.character.components import StatsComponent
    from game.features.player.components import PlayerComponent

    e = Entity()
    e.add(PlayerComponent())
    e.add(TransformComponent(x=100, y=100))
    e.add(VelocityComponent(speed=500))
    e.add(StatsComponent(max_hp=100, attack=10, defense=5, attack_range=10, cooldown=200))
    return e


@pytest.fixture
def enemy_entity():
    """Entité ennemi minimale pour les tests game features."""
    from engine.features.physics.components import TransformComponent, VelocityComponent
    from engine.features.sprite.components import AnimationSetComponent
    from game.features.character.components import StatsComponent, NameComponent
    from game.features.enemy_ai.components import AIComponent

    e = Entity()
    e.add(AIComponent(move_cooldown=1500))
    e.add(TransformComponent(x=200, y=200))
    e.add(VelocityComponent(speed=300))
    e.add(StatsComponent(max_hp=50, attack=5, defense=2, attack_range=8, cooldown=500))
    e.add(NameComponent(name="TestEnemy", entity_type="Demon"))
    e.add(AnimationSetComponent())
    return e
