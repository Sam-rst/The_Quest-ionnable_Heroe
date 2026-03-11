# Proposition B : Architecture Scenes + Managers

## Principe

Architecture classique du jeu video : le jeu est divise en **scenes** (menu, gameplay, game over...) gerees par un **scene manager**. Chaque systeme du jeu (combat, sauvegarde, audio...) est encapsule dans un **manager** independant.

C'est l'approche la plus repandue dans les jeux pygame de taille moyenne.

## Structure proposee

```
src/
├── __init__.py
├── game.py                    # Classe Game : init pygame, lance SceneManager
├── settings.py
│
├── core/                      # Moteur du jeu
│   ├── __init__.py
│   ├── scene.py               # Classe abstraite Scene
│   ├── scene_manager.py       # Empile/depile les scenes
│   ├── event_bus.py           # Systeme d'evenements (publish/subscribe)
│   └── asset_manager.py       # Cache et chargement des assets
│
├── scenes/                    # Chaque ecran = une scene
│   ├── __init__.py
│   ├── menu_scene.py          # Selection de classe
│   ├── gameplay_scene.py      # Boucle de jeu principale
│   ├── merchant_scene.py      # Ecran marchand
│   ├── game_over_scene.py     # Ecran de mort
│   └── intro_scene.py         # Introduction narrative
│
├── entities/
│   ├── __init__.py
│   ├── entity.py              # Classe de base (sprite + position + type)
│   ├── character.py           # Character : movement, animation, stats
│   ├── player.py              # Player + input
│   ├── enemy.py               # Enemy + AI
│   └── npc.py                 # NPC
│
├── managers/                  # Systemes du jeu
│   ├── __init__.py
│   ├── combat_manager.py      # Gere projectiles, degats, collisions combat
│   ├── collision_manager.py   # Collisions tiles + bords de map
│   ├── save_manager.py        # Sauvegarde/chargement JSON
│   ├── spawn_manager.py       # Creation des ennemis/PNJs par map
│   ├── inventory_manager.py   # Inventaire + items
│   └── map_manager.py         # Gestion des maps, teleportation, camera
│
├── world/
│   ├── __init__.py
│   ├── camera.py              # CameraGroup
│   ├── game_map.py            # Carte (chargement TMX)
│   └── teleporter.py          # Teleportation
│
├── combat/
│   ├── __init__.py
│   ├── projectile.py
│   └── weapon.py
│
├── ui/
│   ├── __init__.py
│   ├── hud.py                 # HUD in-game (barres de vie)
│   ├── button.py
│   └── text.py                # Utilitaires de rendu texte
│
├── items/
│   ├── __init__.py
│   ├── item.py
│   └── inventory.py
│
└── data/
    ├── __init__.py
    ├── entity_data.py         # Stats des classes/ennemis (dicts de config)
    └── encoder.py

graphics/
main.py
```

## Concepts cles

### Scene Manager (pile de scenes)

```python
class Scene(ABC):
    def __init__(self, game):
        self.game = game  # reference vers Game pour acceder aux managers

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]): ...

    @abstractmethod
    def update(self, dt: float): ...

    @abstractmethod
    def draw(self, screen: pygame.Surface): ...

    def on_enter(self): ...   # appele quand la scene devient active
    def on_exit(self): ...    # appele quand on quitte la scene


class SceneManager:
    def __init__(self):
        self.stack: list[Scene] = []

    def push(self, scene: Scene):
        scene.on_enter()
        self.stack.append(scene)

    def pop(self) -> Scene:
        scene = self.stack.pop()
        scene.on_exit()
        return scene

    def replace(self, scene: Scene):
        self.pop()
        self.push(scene)

    @property
    def current(self) -> Scene:
        return self.stack[-1]
```

Le marchand devient un `push` (on empile la scene marchand au-dessus du gameplay),
le game over un `replace` (on remplace le gameplay), et le retour au menu un `pop`.

### Event Bus (decouplage)

```python
class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        self._listeners.setdefault(event_type, []).append(callback)

    def publish(self, event_type: str, **data):
        for callback in self._listeners.get(event_type, []):
            callback(**data)
```

Exemples d'evenements :
- `"enemy_killed"` → `SpawnManager` drop un item, `SaveManager` enregistre
- `"player_died"` → `SceneManager` push `GameOverScene`
- `"teleport"` → `MapManager` change la map active

### Spawn Manager (plus de copier-coller dans main.py)

```python
# data/entity_data.py
MAP_SPAWNS = {
    "Watertemple": [
        {"type": "Demon", "count": 2},
        {"type": "Goblin", "count": 2},
        {"type": "Zombie", "count": 1},
        {"type": "Skeleton", "count": 2},
    ],
    "Dungeon": [
        {"type": "Demon", "count": 1},
        # ...
    ],
}

# managers/spawn_manager.py
class SpawnManager:
    def spawn_map(self, map_name, camera_group):
        for spawn_info in MAP_SPAWNS.get(map_name, []):
            for i in range(spawn_info["count"]):
                enemy = EnemyFactory.create(spawn_info["type"], camera_group)
```

### Boucle principale simplifiee

```python
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(...)
        self.clock = pygame.time.Clock()
        self.scene_manager = SceneManager()
        self.save_manager = SaveManager('save.json')
        self.asset_manager = AssetManager()
        self.event_bus = EventBus()
        # ...
        self.scene_manager.push(MenuScene(self))

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            events = pygame.event.get()
            self.scene_manager.current.handle_events(events)
            self.scene_manager.current.update(dt)
            self.scene_manager.current.draw(self.screen)
            pygame.display.flip()
```

## Avantages

| Avantage | Detail |
|----------|--------|
| **Separation claire** | Chaque scene a sa propre logique, son propre rendu |
| **Plus de boucles imbriquees** | Le marchand, game over, menu sont des scenes independantes |
| **Decouplage via EventBus** | Les managers communiquent sans se connaitre |
| **Extensible** | Ajouter une scene (inventaire plein ecran, carte du monde, dialogues) est trivial |
| **Testable** | Chaque manager peut etre teste independamment |
| **Pattern eprouve** | Architecture standard dans l'industrie du jeu indie |

## Inconvenients

| Inconvenient | Detail |
|--------------|--------|
| **Refactoring significatif** | Necessite de reecrire la boucle de jeu et l'init |
| **Plus de fichiers** | ~30 fichiers vs ~20 actuellement |
| **Character toujours monolithique** | La classe Character garde plusieurs responsabilites (sauf si on ajoute des sous-systemes) |
| **Overhead pour un petit jeu** | Le systeme de scenes + event bus peut sembler sur-ingenierie pour un projet de cette taille |
| **Courbe d'apprentissage** | L'equipe doit comprendre les patterns Scene/Manager/EventBus |
