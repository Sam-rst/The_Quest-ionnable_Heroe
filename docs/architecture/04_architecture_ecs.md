# Proposition C : Architecture ECS (Entity-Component-System)

## Principe

L'**ECS** est un paradigme ou :
- Une **Entity** est juste un identifiant (un int)
- Un **Component** est un paquet de donnees sans logique (position, sante, sprite...)
- Un **System** est une fonction qui opere sur les entites possedant certains components

C'est l'approche utilisee par les moteurs modernes (Unity DOTS, Bevy, Amethyst).
L'idee est de privilegier la **composition** sur l'**heritage**.

## Pourquoi c'est pertinent ici

Le probleme principal du projet actuel est l'**heritage profond** :
```
Sprite → Caracter → Player → Warrior
Sprite → Caracter → Ennemy → Demon
Sprite → Caracter → Pnj → Merchant
```

Si on veut un PNJ qui peut combattre, ou un ennemi qui peut parler, l'heritage bloque.
Avec l'ECS, on compose : une entite avec `Health + AI + DialogComponent` est un PNJ combattant parlant.

## Structure proposee

```
src/
├── __init__.py
├── game.py                    # Init pygame, boucle principale
├── settings.py
│
├── ecs/                       # Moteur ECS maison (leger)
│   ├── __init__.py
│   ├── world.py               # World : registre d'entites + components
│   ├── entity.py              # EntityId (alias int) + factory
│   ├── component.py           # Classe de base Component (dataclass)
│   └── system.py              # Classe de base System
│
├── components/                # Donnees pures (pas de logique)
│   ├── __init__.py
│   ├── transform.py           # Position, direction, vitesse
│   ├── sprite_renderer.py     # Image, frames d'animation, scale
│   ├── health.py              # HP, max_HP
│   ├── combat.py              # attack_value, defense_value, range, cooldown
│   ├── input.py               # Marqueur "controlable par le joueur"
│   ├── ai.py                  # Type d'AI (wander, chase, static)
│   ├── collider.py            # Rect de collision, layer
│   ├── projectile.py          # Direction, speed, range, distance_traveled
│   └── inventory.py           # Liste d'items
│
├── systems/                   # Logique pure (pas de donnees)
│   ├── __init__.py
│   ├── input_system.py        # Lit le clavier/souris → modifie Transform
│   ├── ai_system.py           # Wander/Chase → modifie Transform
│   ├── movement_system.py     # Applique velocity * dt → modifie position
│   ├── collision_system.py    # Detecte collisions tiles/entites
│   ├── combat_system.py       # Gere les degats, la mort, les drops
│   ├── projectile_system.py   # Deplace les projectiles, gere les impacts
│   ├── animation_system.py    # Avance les frames selon l'etat
│   ├── render_system.py       # Dessine les sprites + HUD
│   ├── camera_system.py       # Calcule l'offset camera
│   └── save_system.py         # Serialise les components en JSON
│
├── scenes/                    # Scenes (utilisent le World ECS)
│   ├── __init__.py
│   ├── scene.py
│   ├── scene_manager.py
│   ├── menu_scene.py
│   ├── gameplay_scene.py
│   ├── merchant_scene.py
│   └── game_over_scene.py
│
├── factories/                 # Creation d'entites avec les bons components
│   ├── __init__.py
│   ├── player_factory.py      # Cree un joueur (Transform + Sprite + Health + Combat + Input)
│   ├── enemy_factory.py       # Cree un ennemi (Transform + Sprite + Health + Combat + AI)
│   └── npc_factory.py         # Cree un PNJ
│
├── data/
│   ├── __init__.py
│   ├── class_stats.py         # Donnees de config par classe
│   ├── enemy_stats.py         # Donnees par type d'ennemi
│   └── map_spawns.py          # Config des spawns par map
│
├── world/
│   ├── __init__.py
│   ├── game_map.py
│   └── teleporter.py
│
├── ui/
│   ├── __init__.py
│   ├── hud.py
│   └── button.py
│
└── assets/
    ├── __init__.py
    └── asset_manager.py

graphics/
main.py
```

## Concepts cles

### World (registre central)

```python
@dataclass
class World:
    _next_id: int = 0
    _components: dict[type, dict[int, Component]] = field(default_factory=dict)

    def create_entity(self) -> int:
        eid = self._next_id
        self._next_id += 1
        return eid

    def add_component(self, entity: int, component: Component):
        comp_type = type(component)
        self._components.setdefault(comp_type, {})[entity] = component

    def get_component(self, entity: int, comp_type: type[T]) -> T | None:
        return self._components.get(comp_type, {}).get(entity)

    def query(self, *comp_types: type) -> Iterator[tuple[int, ...]]:
        """Retourne les entites qui possedent TOUS les components demandes."""
        if not comp_types:
            return
        first = set(self._components.get(comp_types[0], {}).keys())
        for ct in comp_types[1:]:
            first &= set(self._components.get(ct, {}).keys())
        for eid in first:
            yield (eid, *(self._components[ct][eid] for ct in comp_types))

    def destroy_entity(self, entity: int):
        for comp_dict in self._components.values():
            comp_dict.pop(entity, None)
```

### Components (dataclasses pures)

```python
@dataclass
class Transform(Component):
    x: float = 0
    y: float = 0
    dir_x: float = 0
    dir_y: float = 0
    speed: float = 200

@dataclass
class Health(Component):
    hp: int = 100
    max_hp: int = 100

@dataclass
class Combat(Component):
    attack: int = 10
    defense: int = 5
    range: int = 5
    cooldown_ms: int = 800
    last_shot_ms: int = 0
```

### Systems (logique isolee)

```python
class MovementSystem(System):
    def update(self, world: World, dt: float):
        for eid, transform in world.query(Transform):
            transform.x += transform.dir_x * transform.speed * dt
            transform.y += transform.dir_y * transform.speed * dt

class CombatSystem(System):
    def update(self, world: World, dt: float):
        for eid, health in world.query(Health):
            if health.hp <= 0:
                world.destroy_entity(eid)
                self.event_bus.publish("entity_died", entity=eid)
```

### Factory (remplace les transform_to_xxx)

```python
class PlayerFactory:
    CLASSES = {
        "Warrior": {"hp": 100, "attack": 20, "defense": 10, "speed": 250, "cooldown": 800, "range": 3},
        "Mage":    {"hp": 80,  "attack": 15, "defense": 5,  "speed": 275, "cooldown": 800, "range": 20},
        # ...
    }

    @staticmethod
    def create(world: World, class_name: str, pos: tuple) -> int:
        stats = PlayerFactory.CLASSES[class_name]
        eid = world.create_entity()
        world.add_component(eid, Transform(x=pos[0], y=pos[1], speed=stats["speed"]))
        world.add_component(eid, Health(hp=stats["hp"], max_hp=stats["hp"]))
        world.add_component(eid, Combat(attack=stats["attack"], defense=stats["defense"],
                                        range=stats["range"], cooldown_ms=stats["cooldown"]))
        world.add_component(eid, SpriteRenderer(character_type=class_name.lower()))
        world.add_component(eid, PlayerInput())  # marqueur
        return eid
```

## Avantages

| Avantage | Detail |
|----------|--------|
| **Zero heritage profond** | Plus de hierarchie Caracter → Player → Warrior. Tout est composable |
| **Extensibilite maximale** | Ajouter un systeme (quetes, audio, particules) = creer un System + Component |
| **Pas de duplication** | Les stats sont des donnees, pas du code. Un seul Factory pour toutes les classes |
| **Performance** | Les Systems itèrent sur des donnees contigues, pas sur des arbres d'heritage |
| **Testabilite** | Chaque System est testable isolement avec un World simule |
| **Decouplage total** | Aucun module n'importe un autre sauf via le World |

## Inconvenients

| Inconvenient | Detail |
|--------------|--------|
| **Reecriture quasi-complete** | Tres peu de code existant est reutilisable tel quel |
| **Complexite initiale elevee** | Il faut ecrire le mini-framework ECS avant toute fonctionnalite |
| **Inhabituel en Python/pygame** | L'ECS est plus courant en Rust/C++. Peu d'exemples pygame |
| **Debugging plus abstrait** | Un "Warrior" n'existe pas comme objet, c'est un ensemble de components — plus dur a inspecter |
| **Courbe d'apprentissage forte** | L'equipe doit maitriser un paradigme tres different de l'OOP classique |
| **Overhead conceptuel** | Pour un jeu de cette taille, la flexibilite de l'ECS est probablement disproportionnee |
