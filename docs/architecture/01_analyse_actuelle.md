# Analyse de l'architecture actuelle

## Vue d'ensemble

Le projet est actuellement structuré en **fichiers plats** à la racine, sans packages Python.
Tous les modules sont au même niveau, avec un couplage fort via le module `sprites.py` qui sert d'**état global partagé**.

## Problemes identifies

### 1. `sprites.py` comme etat global

`sprites.py` est importé par quasiment tous les modules. Il contient :
- Tous les groupes de sprites (ennemis, projectiles, items, PNJs...)
- Le dictionnaire `camera_groups` (toutes les maps)
- L'instance `save_data`
- La reference `camera_group` active et `player`

**Consequence** : il est impossible de tester un module de facon isolee, et tout changement dans `sprites.py` impacte l'ensemble du projet.

### 2. `main.py` procedural

La boucle de jeu est entierement procedurale :
- Pas de classe `Game` ou `Engine`
- La logique d'evenements, de rendu, de sauvegarde et de spawn est melangee dans une seule boucle `while True`
- Les ennemis et PNJs sont crees en dur (copier-coller de `Farmer` 12 fois par ex.)

### 3. `images.py` monolithique (~100Ko)

Toutes les frames de sprites sont chargees au demarrage via des variables globales.
Chaque module fait `from images import *`, ce qui :
- Charge **toutes** les images en memoire meme si la map n'en a pas besoin
- Rend difficile l'ajout de nouveaux sprites (fichier enorme)
- Pollue le namespace avec des centaines de variables

### 4. Duplication massive dans les entites

Chaque sous-classe (`Demon`, `Goblin`, `Zombie`, `Skeleton`, `Warrior`, `Mage`...) repete exactement le meme pattern :

```python
def transform_to_xxx(self):
    self.frames['Bottom Walk'] = xxx_bottom_walks
    self.frames['Left Walk'] = xxx_left_walks
    # ... meme structure a chaque fois
    self.set_range(X)
    self.set_max_HP(Y)
    # ... etc
```

Le meme probleme se retrouve dans `encoder.py` ou chaque classe est serialisee avec un bloc `if isinstance(obj, ...)` identique.

### 5. Pas de systeme de scenes/etats

Il n'existe pas de gestion d'etats du jeu. Le menu, le jeu, le game over, le marchand sont geres par des boucles `while True` imbriquees ou des appels bloquants (`menu.run()`, `menu_marchand.run()`).

### 6. Responsabilites melangees dans `Caracter`

`caracter.py` gere a la fois :
- Le mouvement et l'input
- Les collisions (avec les tiles ET les bords de map)
- L'animation (frames, directions)
- Les stats de combat (HP, attaque, defense)
- L'affichage (barre de vie)

### 7. Systeme de sauvegarde fragile

- `SaveData` lit et reecrit le fichier JSON complet a chaque operation
- La sauvegarde est declenchee depuis `main.py`, `carte.py` (game over), `menu.py`, `items.py` — sans centralisation
- `save.json` est supprime brutalement au game over

### 8. Fichiers morts ou inutilises

- `mob.py` : classe vide avec une signature incompatible avec `Caracter`
- `button.py` : script standalone avec sa propre boucle pygame, non integre
- `engine.py` / `test.py` / `tirtest.py` : fichiers de test/prototype non lies au jeu
- `weapon.py` : classe `Weapon` jamais utilisee dans le jeu

## Diagramme des dependances actuelles

```
main.py
├── sprites.py (etat global)
│   ├── camera.py → CameraGroup
│   │   ├── carte.py → Carte (charge TMX)
│   │   ├── collisions.py → CollisionTile
│   │   └── ennemy.py, player.py (pour isinstance)
│   └── save.py → SaveData
├── menu.py → Menu
│   └── player.py → Warrior, Mage, Assassin, Guard, Archer, Tank
├── ennemy.py → Demon, Goblin, Zombie, Skeleton
│   └── caracter.py → Caracter (classe de base)
│       └── images.py (from images import *)
│       └── projectiles.py → Projectile, EnnemiProjectile
├── pnj.py → Merchant, Farmer
├── items.py → Item
└── menu_marchand.py → Menu_Marchand
```

Presque tous les modules importent `sprites` pour acceder a l'etat global, creant des **dependances circulaires implicites**.
