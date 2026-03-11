"""Character factory: création data-driven d'entités depuis les JSON."""

from __future__ import annotations
import json
import logging
import os
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

from engine.core.entity import Entity
from engine.features.physics.components import TransformComponent, VelocityComponent, ColliderComponent
from engine.features.sprite.components import SpriteComponent, AnimationSetComponent
from game.features.character.components import StatsComponent, ClassComponent, NameComponent

if TYPE_CHECKING:
    from engine.features.sprite.asset_loader import AssetLoader

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _load_json(filename: str) -> dict:
    with open(os.path.join(_DATA_DIR, filename), "r") as f:
        return json.load(f)


def create_player(class_name: str, name: str, x: float, y: float,
                  asset_loader: AssetLoader | None = None) -> Entity:
    classes = _load_json("classes.json")
    data = classes[class_name]

    entity = Entity()
    entity.add(NameComponent(name=name, entity_type="Player"))
    entity.add(ClassComponent(class_name=class_name, display_name=data["display_name"]))
    entity.add(StatsComponent(
        max_hp=data["max_hp"], attack=data["attack"], defense=data["defense"],
        attack_range=data["range"], cooldown=data["cooldown"], speed=data["speed"],
    ))
    entity.add(TransformComponent(x=x, y=y))
    entity.add(VelocityComponent(speed=data["speed"]))
    entity.add(ColliderComponent())
    entity.add(SpriteComponent(sprite_id=data["sprite_id"], scale=4))

    anim = AnimationSetComponent()
    anim.speed = data["animation_speed"]
    if asset_loader:
        anim.animations = asset_loader.load_all_animations(data["sprite_id"])
    entity.add(anim)

    logger.info("Player created: %s (%s) at (%.0f, %.0f)", name, class_name, x, y)
    return entity


def create_enemy(enemy_type: str, name: str, x: float, y: float,
                 asset_loader: AssetLoader | None = None) -> Entity:
    enemies = _load_json("enemies.json")
    data = enemies[enemy_type]

    entity = Entity()
    entity.add(NameComponent(name=name, entity_type=enemy_type))
    entity.add(StatsComponent(
        max_hp=data["max_hp"], attack=data["attack"], defense=data["defense"],
        attack_range=data["range"], cooldown=data["cooldown"], speed=data["speed"],
    ))
    entity.add(TransformComponent(x=x, y=y))
    entity.add(VelocityComponent(speed=data["speed"]))
    entity.add(ColliderComponent())
    entity.add(SpriteComponent(sprite_id=data["sprite_id"], scale=4))

    from game.features.enemy_ai.components import AIComponent
    entity.add(AIComponent(move_cooldown=data["move_cooldown"]))

    anim = AnimationSetComponent()
    anim.speed = data["animation_speed"]
    if asset_loader:
        anim.animations = asset_loader.load_all_animations(data["sprite_id"])
    entity.add(anim)

    logger.debug("Enemy created: %s (%s) at (%.0f, %.0f)", name, enemy_type, x, y)
    return entity


def create_npc(npc_type: str, name: str, x: float, y: float,
               asset_loader: AssetLoader | None = None) -> Entity:
    npcs = _load_json("npcs.json")
    data = npcs[npc_type]

    entity = Entity()
    entity.add(NameComponent(name=name, entity_type=npc_type))
    entity.add(StatsComponent(
        max_hp=data["max_hp"], attack=data["attack"], defense=data["defense"],
        attack_range=data["range"], cooldown=data["cooldown"], speed=data["speed"],
    ))
    entity.add(TransformComponent(x=x, y=y))
    entity.add(VelocityComponent(speed=data["speed"]))
    entity.add(ColliderComponent())
    entity.add(SpriteComponent(sprite_id=data["sprite_id"], scale=4))

    from game.features.npc.components import NPCComponent
    entity.add(NPCComponent(
        npc_type=npc_type,
        interactable=data.get("interactable", False),
        wanders=data.get("wanders", False),
        move_cooldown=data.get("move_cooldown", 1500),
    ))

    anim = AnimationSetComponent()
    anim.speed = data["animation_speed"]
    if asset_loader:
        anim.animations = asset_loader.load_all_animations(data["sprite_id"])
    entity.add(anim)

    logger.debug("NPC created: %s (%s) at (%.0f, %.0f)", name, npc_type, x, y)
    return entity
