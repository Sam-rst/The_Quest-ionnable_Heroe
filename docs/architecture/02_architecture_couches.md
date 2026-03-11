# Proposition A : Architecture en couches (Layered)

## Principe

Reorganiser le code existant en **packages thematiques** sans changer fondamentalement la logique du jeu.
C'est le refactoring le moins risque : on deplace les fichiers, on decoupe les gros modules, et on clarifie les responsabilites.

## Structure proposee

```
src/
├── __init__.py
├── game.py                  # Classe Game (boucle principale)
├── settings.py              # Constantes globales
│
├── entities/                # Tout ce qui est "vivant"
│   ├── __init__.py
│   ├── character.py         # Classe de base Character
│   ├── player.py            # Player + sous-classes (Warrior, Mage...)
│   ├── enemy.py             # Enemy + sous-classes (Demon, Goblin...)
│   └── npc.py               # NPC + sous-classes (Merchant, Farmer)
│
├── combat/                  # Systeme de combat
│   ├── __init__.py
│   ├── projectile.py        # Projectile + EnemyProjectile
│   ├── weapon.py            # Weapon
│   └── dice.py              # Dice, RiggedDice
│
├── world/                   # Tout ce qui concerne le monde/maps
│   ├── __init__.py
│   ├── camera.py            # CameraGroup
│   ├── map.py               # Carte (renomme de carte.py)
│   ├── collision.py         # CollisionTile
│   └── teleportation.py     # Teleportation (extrait de carte.py)
│
├── ui/                      # Interface utilisateur
│   ├── __init__.py
│   ├── menu.py              # Menu principal / selection de classe
│   ├── merchant_menu.py     # Menu marchand
│   ├── hud.py               # Barres de vie, debug overlay
│   ├── button.py            # Composant Button reutilisable
│   └── introduction.py      # Ecran d'intro
│
├── items/                   # Objets et inventaire
│   ├── __init__.py
│   ├── item.py              # Item de base
│   └── inventory.py         # Inventaire
│
├── data/                    # Persistence
│   ├── __init__.py
│   ├── save_manager.py      # SaveData refactorise
│   └── encoder.py           # Encodeur JSON (generique)
│
└── assets/                  # Chargement des ressources
    ├── __init__.py
    └── sprite_loader.py     # Remplacement de images.py
                             # (charge les sprites a la demande)

graphics/                    # Inchange (assets bruts)
main.py                      # Point d'entree : from src.game import Game
```

## Changements cles

### Remplacement de `sprites.py` par injection

Au lieu d'un module global, la classe `Game` possede les groupes de sprites et les passe en parametre :

```python
class Game:
    def __init__(self):
        self.sprite_groups = SpriteGroups()  # contient tous les groupes
        self.save_data = SaveManager('save.json')
        self.camera_groups = self._create_maps()
        self.active_camera = self.camera_groups["Overworld"]
        self.player = None

    def run(self):
        menu = Menu(self)
        self.player = menu.run()
        while self.running:
            self.handle_events()
            self.update(dt)
            self.draw()
```

### Decoupage de `images.py`

`sprite_loader.py` charge les sprites par entite, a la demande :

```python
def load_character_frames(character_type: str) -> dict[str, list[Surface]]:
    """Charge les frames walk/attack pour un type de personnage."""
    base_path = f"graphics/caracters/{character_type}"
    return {
        "Bottom Walk": load_animation(f"{base_path}/bottom_walk"),
        "Top Walk": load_animation(f"{base_path}/top_walk"),
        # ...
    }
```

### Elimination de la duplication dans les entites

Les stats et frames sont definies via des **donnees de configuration** plutot que du code :

```python
# Dans un dict ou fichier JSON/TOML
PLAYER_CLASSES = {
    "Warrior": {"hp": 100, "attack": 20, "defense": 10, "speed": 250, "cooldown": 800, "range": 3},
    "Mage":    {"hp": 80,  "attack": 15, "defense": 5,  "speed": 275, "cooldown": 800, "range": 20},
    # ...
}
```

### Encodeur generique

```python
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Player):
            return {
                "Class": obj.get_type(),
                "Name": obj.get_name(),
                "Max HP": obj.get_max_HP(),
                # ... une seule fois pour toutes les classes
            }
```

## Avantages

| Avantage | Detail |
|----------|--------|
| **Faible risque** | On deplace et reorganise sans reecrire la logique |
| **Progressif** | Peut etre fait module par module |
| **Facile a comprendre** | Structure intuitive par domaine |
| **Compatible** | Le code pygame reste identique, seules les imports changent |

## Inconvenients

| Inconvenient | Detail |
|--------------|--------|
| **Couplage residuel** | Les entites accedent encore directement aux groupes de sprites |
| **Pas de scenes** | Toujours des boucles imbriquees pour menu/jeu/game over |
| **Scalabilite limitee** | Ajouter un nouveau systeme (quetes, dialogue, audio) necessite de modifier `Game` |
| **Character reste gros** | La classe de base fait toujours mouvement + collision + animation + combat |
