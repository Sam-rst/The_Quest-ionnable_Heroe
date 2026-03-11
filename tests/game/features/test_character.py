"""Tests pour game.features.character."""

import pytest
from engine.core.entity import Entity
from engine.features.physics.components import TransformComponent, VelocityComponent, ColliderComponent
from engine.features.sprite.components import SpriteComponent, AnimationSetComponent
from game.features.character.components import StatsComponent, ClassComponent, NameComponent
from game.features.character.factory import create_player, create_enemy


class TestStatsComponent:
    def test_defaults(self):
        s = StatsComponent()
        assert s.max_hp == 1
        assert s.hp == 1
        assert s.attack == 1

    def test_custom(self):
        s = StatsComponent(max_hp=100, attack=20, defense=10)
        assert s.max_hp == 100
        assert s.hp == 100
        assert s.attack == 20

    def test_is_alive_hp_positive(self):
        s = StatsComponent(max_hp=10)
        assert s.is_alive()

    def test_is_alive_hp_zero(self):
        s = StatsComponent(max_hp=10)
        s.hp = 0
        assert not s.is_alive()

    def test_take_damage(self):
        s = StatsComponent(max_hp=100)
        s.take_damage(30)
        assert s.hp == 70

    def test_take_damage_not_negative(self):
        s = StatsComponent(max_hp=10)
        s.take_damage(999)
        assert s.hp == 0

    def test_heal(self):
        s = StatsComponent(max_hp=100)
        s.take_damage(50)
        s.heal(20)
        assert s.hp == 70

    def test_heal_capped_at_max(self):
        s = StatsComponent(max_hp=100)
        s.take_damage(10)
        s.heal(999)
        assert s.hp == 100

    def test_regenerate(self):
        s = StatsComponent(max_hp=100)
        s.take_damage(50)
        s.regenerate()
        assert s.hp == 100


class TestClassComponent:
    def test_fields(self):
        c = ClassComponent(class_name="Mage", display_name="Mage")
        assert c.class_name == "Mage"
        assert c.display_name == "Mage"


class TestNameComponent:
    def test_fields(self):
        n = NameComponent(name="Hero", entity_type="Player")
        assert n.name == "Hero"
        assert n.entity_type == "Player"


class TestFactory:
    def test_create_player_warrior(self):
        player = create_player("Warrior", "TestHero", 100, 200)
        assert player.has(NameComponent, ClassComponent, StatsComponent,
                          TransformComponent, VelocityComponent, SpriteComponent)
        assert player.get(NameComponent).name == "TestHero"
        assert player.get(ClassComponent).class_name == "Warrior"
        assert player.get(TransformComponent).x == 100

    def test_create_player_unknown_class_uses_defaults(self):
        player = create_player("UnknownClass", "Test", 0, 0)
        stats = player.get(StatsComponent)
        assert stats is not None
        assert stats.max_hp > 0

    def test_create_player_without_asset_loader(self):
        player = create_player("Warrior", "Test", 0, 0, asset_loader=None)
        anim = player.get(AnimationSetComponent)
        assert anim is not None
        assert anim.animations == {}

    def test_create_enemy(self):
        enemy = create_enemy("Demon", "TestDemon", 50, 50)
        assert enemy.has(StatsComponent, TransformComponent)
        stats = enemy.get(StatsComponent)
        assert stats.max_hp > 0

    @pytest.mark.parametrize("class_name", [
        "Warrior", "Mage", "Archer", "Healer", "Necromancer", "Assassin"
    ])
    def test_all_player_classes(self, class_name):
        player = create_player(class_name, "Test", 0, 0)
        assert player.has(StatsComponent)
        assert player.get(StatsComponent).max_hp > 0
