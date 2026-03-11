# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Quest-ionnable Heroe** is a 2D top-down RPG built with **pygame** and **pytmx**. The game uses a feature-based ECS-like architecture with separated logic/rendering, enabling headless execution and future multiplayer.

## Running the Game

```bash
uv sync          # Install dependencies (pygame, pytmx)
uv run main.py   # Launch the game
```

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/).

## Project Structure

```
The_Quest-ionnable_Heroe/
├── main.py                     # Entry point (5 lines)
├── pyproject.toml              # hatchling build with src-layout
├── src/
│   ├── engine/                 # Reusable engine (no game-specific code)
│   └── game/                   # Game-specific code
├── assets/                     # All game assets
│   ├── manifest.json           # Sprite registry
│   ├── sprites/                # Characters, items, weapons, potions
│   ├── maps/                   # TMX, TSX, tilesets, exports
│   ├── fonts/                  # Enchanted_Land.otf
│   └── raw/                    # Source files (LPC, PSD, Tiled project)
├── saves/                      # Save data (auto-generated)
└── docs/                       # Documentation
```

## Architecture

### Entry Point

`main.py` → `src/game/app.py:create_game()` — Initializes pygame, creates Game instance, runs menu scene then gameplay scene.

### Engine (`src/engine/`) — Reusable across projects

```
src/engine/
├── core/
│   ├── entity.py          # Entity: ID + dict of Components
│   ├── component.py       # Component base class (pure data)
│   ├── world.py           # World: entity storage + queries by component type
│   ├── event_bus.py       # Publish/subscribe for feature decoupling
│   ├── system.py          # System + Feature base classes
│   ├── game.py            # Game: main loop, system/feature registry
│   └── time_manager.py    # Time management without pygame
│
└── features/
    ├── physics/            # TransformComponent, VelocityComponent, ColliderComponent
    ├── input/              # InputAction enum, InputMap, InputState + PygameAdapter
    ├── scene/              # Scene ABC, SceneManager (push/pop stack)
    ├── tilemap/            # TMX parsing → pure data + TilemapRenderer
    ├── camera/             # CameraState (center/box modes) + renderer
    ├── sprite/             # AssetLoader (manifest.json), AnimationController, SpriteRenderer
    ├── save/               # SaveManager + JsonBackend
    └── ui/                 # UIElement, Button, Label, ProgressBar widgets
```

**Rule: No `import pygame` in `logic.py`, `components.py`, or `factory.py` files.**

### Game (`src/game/`) — Specific to The Quest-ionnable Heroe

```
src/game/
├── app.py                 # Creates Game, registers features, main loop
├── settings.py            # Constants (SCALE=4, FPS=60, paths)
│
└── features/
    ├── character/         # StatsComponent, ClassComponent, data-driven factory
    │   ├── factory.py     # create_player/enemy/npc from JSON
    │   └── data/          # classes.json, enemies.json, npcs.json
    ├── player/            # PlayerSystem (input → movement/shooting)
    ├── enemy_ai/          # EnemyAISystem (wander, shoot toward player)
    ├── npc/               # NPCSystem (wander, interaction)
    ├── combat/            # CombatSystem (projectile spawn, trajectory, damage)
    ├── inventory/         # InventorySystem (item drops, pickup)
    ├── shop/              # ShopSystem (buy/sell via trades)
    ├── world_map/         # WorldMapSystem (map transitions, spawns)
    │   └── data/          # maps.json, spawns.json
    ├── main_menu/         # MainMenuScene (class selection)
    ├── game_over/         # GameOverScene (respawn)
    └── gameplay/          # GameplayScene (orchestrates all systems)
```

### Assets (`assets/`)

```
assets/
├── manifest.json           # Sprite registry: sprite_id → file paths
├── sprites/
│   ├── characters/         # player/, ennemy/, npc/, base/
│   ├── items/              # piece/
│   ├── weapons/            # bow/, orbs/
│   └── potions/
├── maps/
│   ├── tmx/                # Map files (6 maps)
│   ├── tsx/                # Tileset definitions
│   ├── tilesets/           # Tileset images (Catacombes/, world/)
│   └── exports/            # Map exports (PNG, JSON)
├── fonts/
│   └── Enchanted_Land.otf
└── raw/                    # Source files (not used at runtime)
    ├── lpc/                # LPC art assets
    ├── psd/                # Photoshop source files
    └── tiled-project/      # .tiled-project, .tiled-session
```

### Data-Driven Design

Stats and configurations are in JSON files, not code:
- `src/game/features/character/data/classes.json` — 6 player classes (Warrior, Mage, etc.)
- `src/game/features/character/data/enemies.json` — 4 enemy types
- `src/game/features/character/data/npcs.json` — NPC definitions
- `src/game/features/world_map/data/maps.json` — Map configs + teleporters
- `src/game/features/world_map/data/spawns.json` — Enemy/NPC spawn definitions
- `assets/manifest.json` — Asset file paths

### Communication Between Features

Features communicate via `EventBus` (never import each other):
- `entity_killed` → InventorySystem drops item, SaveManager persists
- `player_died` → GameplayScene triggers GameOverScene
- `player_shoot` / `enemy_shoot` → CombatSystem creates projectile
- Teleportation is handled by GameplayScene checking teleporter zones

### Legacy Code (to be removed)

Old files in root (`sprites.py`, `images.py`, `camera.py`, `carte.py`, `caracter.py`, `player.py`, `ennemy.py`, `pnj.py`, etc.) are the previous monolithic architecture. `main_old.py` is the backup. These files are no longer used by the new `main.py`.

### Controls

- **ZQSD** — Movement (French AZERTY layout)
- **Left click** — Shoot projectile
- **E** — Interact (teleporters)
- **A** — Pick up items
- **R** — Open merchant menu (near merchant)
- **1** — Use potion
- **ESC** — Save and quit
- **SPACE/E** — Respawn on game over

### Save System

Save data persists to `saves/save.json` (auto-save every 5s, save on quit). Deleted on game over.

### Verification

```bash
# Logic runs without pygame display:
python -c "from engine.core.world import World; print('OK')"

# No pygame in logic files:
grep -rl "import pygame" src/engine/core/ src/game/features/*/components.py src/game/features/*/logic.py
# Should return nothing
```
