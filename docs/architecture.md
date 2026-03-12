# Architecture & Guide du développeur

Ce document décrit l'architecture du projet, les patterns en place, et les conventions à suivre pour ajouter de nouvelles features.

---

## Vue d'ensemble

Le projet sépare **engine** (réutilisable, sans code spécifique au jeu) et **game** (spécifique à The Quest-ionnable Heroe). Chaque couche utilise une architecture ECS-like (Entity-Component-System) avec une séparation stricte logique/rendu.

```
main.py → game/app.py:create_game()
              │
              ├─ Engine (src/engine/)   ← Réutilisable pour d'autres jeux
              │   ├─ core/              ← ECS, event bus, game loop
              │   └─ features/          ← Modules engine (physics, input, save…)
              │
              └─ Game (src/game/)       ← Spécifique au jeu
                  ├─ app.py             ← Initialisation, boucle principale
                  ├─ settings.py        ← Constantes
                  └─ features/          ← Fonctionnalités du jeu
```

---

## Concepts fondamentaux

### Entity-Component-System (ECS-like)

| Concept | Fichier | Rôle |
|---------|---------|------|
| **Entity** | `engine/core/entity.py` | ID unique + dictionnaire de Components. Pas de logique. |
| **Component** | `engine/core/component.py` | Classe de base, pure data. Chaque composant porte des données. |
| **System** | `engine/core/system.py` | Classe abstraite. Traite les entités possédant certains composants chaque frame. |
| **World** | `engine/core/world.py` | Stocke les entités, permet les requêtes par type de composant. |
| **Game** | `engine/core/game.py` | Agrège World + EventBus + TimeManager + Systems. |

**Cycle de vie d'une frame :**
```
Game.update(dt)
  └─ Pour chaque System enregistré → system.update(dt)
       └─ Le System query le World pour les entités qui l'intéressent
            └─ Modifie les Components des entités matchées
```

**Exemple — requêter des entités :**
```python
# Tous les ennemis vivants avec position et vélocité
for entity in world.query(AIComponent, TransformComponent, VelocityComponent):
    ai = entity.get(AIComponent)
    transform = entity.get(TransformComponent)
    # ...
```

### EventBus (pub/sub)

Les features ne s'importent **jamais** entre elles. Elles communiquent par événements :

```python
# Émettre (dans CombatSystem)
self.game.event_bus.emit("entity_killed", entity=e, name="Goblin", x=100, y=200, map_name="Overworld")

# Écouter (dans InventorySystem.on_enter)
self.game.event_bus.subscribe("entity_killed", self._on_entity_killed)
```

**Événements existants :**

| Événement | Émetteur | Payload | Consommateurs |
|-----------|----------|---------|---------------|
| `player_shoot` | PlayerSystem | `entity`, `mouse_pos` | CombatSystem |
| `enemy_shoot` | EnemyAISystem | `entity`, `target_x`, `target_y` | CombatSystem |
| `entity_killed` | EnemyAISystem | `entity`, `name`, `x`, `y`, `map_name` | InventorySystem, GameplayScene (save) |
| `player_died` | CombatSystem, PlayerSystem | `entity` | GameplayScene (game over) |

### Séparation logique / rendu

Chaque feature suit cette structure :

```
feature_name/
├── __init__.py          # Vide (package marker)
├── components.py        # Components — pure data, PAS de pygame
├── logic.py             # System — logique, PAS de pygame
├── renderer.py          # Rendu pygame — imports pygame autorisés
├── factory.py           # (optionnel) Création d'entités, PAS de pygame
└── data/                # (optionnel) Fichiers JSON de config
```

**Règle stricte** : `components.py`, `logic.py` et `factory.py` ne doivent **jamais** faire `import pygame`. Cela garantit que toute la logique tourne headless (tests, serveur multijoueur futur).

---

## Architecture détaillée

### Engine Core (`src/engine/core/`)

#### Entity (`entity.py`)
```python
entity = Entity()              # ID auto-incrémenté
entity.add(TransformComponent(x=100, y=200))  # Chaînable (retourne self)
entity.get(TransformComponent)  # → instance ou None
entity.has(TransformComponent, VelocityComponent)  # → bool
entity.remove(TransformComponent)  # → composant retiré ou None
```

Le `component.entity` est automatiquement mis à jour par `add()` et `remove()`.

#### World (`world.py`)
```python
world = World()
entity = world.create_entity()          # Crée + stocke
world.add_entity(existing_entity)       # Stocke un Entity existant
world.remove_entity(entity_id)          # Retire par ID
world.query(CompA, CompB)              # → Iterator[Entity] ayant TOUS les composants
world.query_one(CompA)                 # → premier match ou None
len(world)                              # → nombre d'entités
world.clear()                           # Vide tout
```

⚠️ **Ne pas supprimer d'entités pendant un `world.query()`** — collecte les IDs à supprimer dans une liste et les retire après la boucle.

#### System (`system.py`)
```python
class MySystem(System):
    def on_enter(self) -> None:
        # Appelé une fois à l'enregistrement (subscribe events ici)
        self.game.event_bus.subscribe("my_event", self._on_event)

    def update(self, dt: float) -> None:
        # Appelé chaque frame par Game.update()
        for entity in self.game.world.query(MyComponent):
            # ...
```

`self.game` est injecté par `Game.add_system()` avant `on_enter()`.

#### Feature (`system.py`)
```python
class MyFeature(Feature):
    def register(self, game: Game) -> None:
        # Enregistre les systèmes, event listeners, etc.
        game.add_system(MySystem())
```

#### TimeManager (`time_manager.py`)
- Indépendant de pygame (`time.time()` pur)
- `game.time.tick()` → retourne dt (secondes)
- `game.time.ticks` → temps écoulé en millisecondes
- `game.time.dt` → dernier dt

### Engine Features (`src/engine/features/`)

#### Physics
- **TransformComponent** : `x`, `y`, `old_x`, `old_y` + `save_old()`
- **VelocityComponent** : `dx`, `dy`, `speed` + `magnitude` property + `normalize()`
- **ColliderComponent** : `width`, `height`, `offset_x`, `offset_y` + propriétés AABB (`left`, `right`, `top`, `bottom`)
- **PhysicsSystem** : intègre vélocité dans la position (`x += dx * speed * dt`)
- **`aabb_overlap(c1, c2)`** : détection de collision AABB

#### Input
- **InputAction** (enum) : `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `SHOOT`, `INTERACT`, `PICKUP`, `OPEN_SHOP`, `USE_POTION`, `ESCAPE`, `CONFIRM`
- **InputState** : état courant (pressed, just_pressed, mouse)
- **InputMap** : lie un keycode pygame à un InputAction
- **PygameInputAdapter** : convertit les événements pygame en InputState

#### Scene
- **Scene** (ABC) : `on_enter()`, `update(dt)`, `render()`, `on_exit()`, `handle_events(events)`
- **SceneManager** : pile de scènes avec `push()`, `pop()`, `replace()`

#### Sprite
- **SpriteComponent** : `sprite_id`, `scale`, `visible`, `layer`, `image`
- **AnimationSetComponent** : `animations` dict, `current_animation`, `frame_index`, `speed`, `is_playing`, `is_attack`
- **AssetLoader** : charge les sprites depuis `manifest.json` avec cache
- **`update_animation()`** : avance les frames d'animation

#### Tilemap
- **TilemapData** (dataclass) : données pures extraites d'un fichier TMX (tiles, collisions, waypoints, téléporteurs)
- **TileRect, Waypoint, TeleporterData** : types de données
- **`parse_tmx()`** : parse un .tmx avec pytmx → retourne TilemapData
- **TilemapRenderer** : dessine les couches de tiles

#### Camera
- **CameraState** : `offset_x`, `offset_y` avec 2 modes : `"center"` (suit la cible) et `"box"` (dead-zone)

#### Save
- **SaveBackend** (ABC) : interface de persistance
- **JsonBackend** : implémentation fichier JSON
- **SaveManager** : `get()`, `set()`, `save()`, `reload()`, `delete()`

#### UI
- **UIElement** : base avec `x`, `y`, `width`, `height`, `visible`, `contains_point()`
- **Button, Label, ProgressBar** : widgets concrets

---

## Game Features (`src/game/features/`)

### Character
- **StatsComponent** : `max_hp`, `hp`, `attack`, `defense`, `attack_range`, `cooldown`, `speed` + `is_alive()`, `take_damage()`, `heal()`, `regenerate()`
- **ClassComponent** : `class_name`, `display_name`
- **NameComponent** : `name`, `entity_type`
- **Factory** (`factory.py`) : `create_player()`, `create_enemy()`, `create_npc()` — crée des entités complètes depuis les JSON
- **Data** : `classes.json` (6 classes), `enemies.json` (4 types), `npcs.json`

### Player
- **PlayerComponent** : `is_teleporting`, `current_map`
- **PlayerSystem** : lit `InputState` → mouvement ZQSD, normalisation diagonale, tir souris, détection de mort

### Enemy AI
- **AIComponent** : `move_cooldown`, `last_move_time`, `current_map`
- **EnemyAISystem** : errance aléatoire, tir vers le joueur, détection de mort → `entity_killed`

### NPC
- **NPCComponent** : `npc_type`, `interactable`, `wanders`, `move_cooldown`, `current_map`
- **NPCSystem** : errance optionnelle, filtrage par map

### Combat
- **ProjectileComponent** : `owner_id`, `dx`, `dy`, `speed`, `attack_range`, `damage`, `is_enemy`, `distance_traveled`
- **CombatSystem** : écoute `player_shoot`/`enemy_shoot`, crée des projectiles, gère trajectoire, collision (distance euclidienne), dégâts, expiration

### Inventory
- **InventoryComponent** : `items` list + `add_item()`, `remove_item()`, `count()`
- **DroppedItemComponent** : `item_name`, `current_map`, animation
- **InventorySystem** : écoute `entity_killed`, crée un drop au sol

### Shop
- **`load_shop_config()`** : charge `shop_config.json`
- **`try_purchase()`** : vérifie l'inventaire et effectue l'échange

### World Map
- **`load_maps_config()`** / **`load_spawns_config()`** : JSON des maps et spawns
- **WorldMapSystem** : gère les transitions entre maps, spawns d'ennemis/NPC

### Scenes
- **MainMenuScene** : sélection de classe avec boutons
- **GameplayScene** : orchestre tous les systèmes, tilemap, caméra, rendu, sauvegarde
- **GameOverScene** : écran game over, relance le menu

---

## Patterns et conventions

### 1. Nommage des fichiers

| Fichier | Contenu | Imports pygame ? |
|---------|---------|:----------------:|
| `components.py` | Classes Component (pure data) | ❌ |
| `logic.py` | System / fonctions métier | ❌ |
| `factory.py` | Création d'entités | ❌ |
| `renderer.py` | Dessin pygame | ✅ |
| `data/*.json` | Données de configuration | — |

### 2. Création d'une entité

Toujours via une factory ou directement dans le System/Scene :
```python
entity = Entity()
entity.add(TransformComponent(x=100, y=200))
entity.add(VelocityComponent(speed=500))
entity.add(StatsComponent(max_hp=50, attack=10))
entity.add(SpriteComponent(sprite_id="goblin", scale=4))
world.add_entity(entity)
```

### 3. Suppression sécurisée d'entités

**Ne jamais** appeler `world.remove_entity()` pendant un `world.query()`. Pattern correct :
```python
to_remove = []
for entity in world.query(MyComponent):
    if should_remove(entity):
        to_remove.append(entity.id)
for eid in to_remove:
    world.remove_entity(eid)
```

### 4. Communication inter-features

**Jamais** d'import direct entre features. Utiliser l'EventBus :
```python
# ❌ INTERDIT
from game.features.inventory.logic import InventorySystem

# ✅ CORRECT
self.game.event_bus.emit("entity_killed", entity=e, ...)
```

### 5. Data-driven design

Les statistiques, configurations et spawns sont dans des fichiers JSON, pas dans le code. Pour ajouter un nouvel ennemi, il suffit d'ajouter une entrée dans `enemies.json` et `spawns.json`.

### 6. Chargement JSON avec error handling

Pattern standard pour les fichiers de configuration :
```python
import json, os, logging
logger = logging.getLogger(__name__)
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def _load_json(filename: str) -> dict:
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Fichier introuvable: %s", path)
        return {}
    except json.JSONDecodeError:
        logger.error("Fichier corrompu: %s", path)
        return {}
```

### 7. Gestion du temps et des cooldowns

Le temps est en millisecondes via `game.time.ticks`. Pattern cooldown :
```python
if ticks - stats.last_shot_time > stats.cooldown:
    # Action
    stats.last_shot_time = ticks
```

### 8. Filtrage par map

Les entités existent dans le World global mais sont filtrées par `current_map` :
```python
if ai.current_map != player_map:
    velocity.dx = 0
    velocity.dy = 0
    continue
```

### 9. Logging

Chaque module crée son logger :
```python
import logging
logger = logging.getLogger(__name__)
```
- `logger.debug()` : détails de gameplay (tirs, spawns, collisions)
- `logger.info()` : événements importants (création joueur, changement de map)
- `logger.error()` : erreurs de config (JSON manquant/corrompu)

### 10. Tests

Les tests sont dans `tests/` et mirrorent la structure `src/` :
```bash
uv run pytest              # 216 tests, ~1s
uv run pytest -v           # Mode verbose
uv run pytest tests/engine/core/test_entity.py  # Un fichier
```
- Les Systems sont testés dans un `Game()` headless (sans pygame)
- `tmp_path` pour les tests fichiers
- `monkeypatch` pour mocker `_DATA_DIR` dans les tests de chargement JSON
- `@pytest.mark.parametrize` pour les variations (6 classes joueur, etc.)

---

## Guide : Ajouter une nouvelle feature

Exemple concret : on veut ajouter un système de **quêtes**.

### Étape 1 — Créer la structure

```
src/game/features/quest/
├── __init__.py          # Vide
├── components.py        # QuestComponent, QuestLogComponent
├── logic.py             # QuestSystem
├── renderer.py          # Affichage UI des quêtes
└── data/
    └── quests.json      # Définitions des quêtes
```

### Étape 2 — Définir les components (`components.py`)

```python
"""Quest components."""
from engine.core.component import Component

class QuestLogComponent(Component):
    def __init__(self) -> None:
        self.active_quests: list[str] = []
        self.completed_quests: list[str] = []

    def accept(self, quest_id: str) -> None:
        if quest_id not in self.active_quests:
            self.active_quests.append(quest_id)

    def complete(self, quest_id: str) -> None:
        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)
            self.completed_quests.append(quest_id)
```

### Étape 3 — Écrire le System (`logic.py`)

```python
"""QuestSystem: gère la progression des quêtes."""
import logging
from engine.core.system import System
from game.features.quest.components import QuestLogComponent

logger = logging.getLogger(__name__)

class QuestSystem(System):
    def __init__(self) -> None:
        self._pending_kills: list[dict] = []

    def on_enter(self) -> None:
        # S'abonner aux événements pertinents
        self.game.event_bus.subscribe("entity_killed", self._on_kill)

    def _on_kill(self, entity, name, **kw) -> None:
        self._pending_kills.append({"name": name})

    def update(self, dt: float) -> None:
        # Traiter les kills en attente
        for kill in self._pending_kills:
            # Vérifier si un kill fait avancer une quête
            pass
        self._pending_kills.clear()
```

### Étape 4 — Enregistrer dans GameplayScene

Dans `src/game/features/gameplay/scene.py`, dans `on_enter()` :

```python
from game.features.quest.logic import QuestSystem
from game.features.quest.components import QuestLogComponent

# Ajouter le component au joueur
self.player_entity.add(QuestLogComponent())

# Enregistrer le système
quest_system = QuestSystem()
self.game.add_system(quest_system)
```

### Étape 5 — Écrire les tests

```python
# tests/game/features/test_quest.py
from engine.core.game import Game
from game.features.quest.components import QuestLogComponent
from game.features.quest.logic import QuestSystem

class TestQuestLogComponent:
    def test_accept(self):
        ql = QuestLogComponent()
        ql.accept("kill_10_goblins")
        assert "kill_10_goblins" in ql.active_quests

class TestQuestSystem:
    def test_entity_killed_tracked(self):
        game = Game()
        game.add_system(QuestSystem())
        game.event_bus.emit("entity_killed", entity=None, name="Goblin",
                            x=0, y=0, map_name="Overworld")
        game.update(0.016)
        # Vérifier le comportement...
```

### Étape 6 — Ajouter le rendu (optionnel)

Dans `renderer.py`, utiliser pygame pour dessiner l'UI des quêtes. Ce fichier est le seul autorisé à importer pygame.

### Étape 7 — Données JSON (optionnel)

```json
// data/quests.json
{
  "kill_10_goblins": {
    "name": "Chasseur de Gobelins",
    "objective": "kill",
    "target": "Goblin",
    "count": 10,
    "reward": "Potion"
  }
}
```

### Checklist

- [ ] `components.py` — pas d'import pygame
- [ ] `logic.py` — pas d'import pygame
- [ ] Communication via EventBus, pas d'import d'autres features
- [ ] Suppression d'entités différée (pas pendant `query()`)
- [ ] Error handling sur les chargements JSON
- [ ] Logger créé avec `logging.getLogger(__name__)`
- [ ] Tests écrits dans `tests/game/features/test_<feature>.py`
- [ ] System enregistré via `game.add_system()` dans GameplayScene

---

## Boucle principale

```
main.py
  │ parse --debug
  │ setup_logging()
  └─ create_game(debug)      [app.py]
       │
       ├─ pygame.init()
       ├─ DebugOverlay (F3 cycle: OFF → TEXT → VISUAL → ALL)
       ├─ Game() + SaveManager + AssetLoader + InputMap
       │
       ├─ MainMenuScene (blocking loop until class selected)
       │
       └─ Main Loop:
            ├─ dt = game.time.tick()
            ├─ Process events (quit, F3, input)
            │
            ├─ if GameplayScene:
            │    ├─ handle_events() → ESC/E/A/R/1
            │    ├─ update(dt) → game.update(dt) → tous les Systems
            │    └─ render() → background → tilemap → entities (tri Y) → health bars
            │
            ├─ elif GameOverScene:
            │    ├─ handle_events() → SPACE/E → respawn
            │    └─ render() → "Game Over"
            │
            ├─ debug_overlay.render() → par-dessus tout
            └─ pygame.display.update()
```

---

## Debug (F3)

Le debug visuel est disponible à tout moment via F3, même sans `--debug` :

| F3 | Niveau | Affichage |
|----|--------|-----------|
| ×1 | TEXT | FPS, entités, position, map |
| ×2 | VISUAL | Hitboxes colorées, zones téléporteurs, vecteurs vélocité, stats entités |
| ×3 | ALL | Texte + visuel |
| ×4 | OFF | Rien |

Lancer avec `--debug` démarre directement au niveau 3 (ALL).
