"""GameplayScene: orchestre tous les systèmes pendant le jeu."""

import logging
import pygame
import sys
import math

logger = logging.getLogger(__name__)

from engine.features.scene.logic import Scene
from engine.features.input.logic import InputAction, InputState
from engine.features.camera.logic import CameraState
from engine.features.tilemap.logic import parse_tmx, TilemapData
from engine.features.tilemap.renderer import TilemapRenderer
from engine.features.sprite.components import SpriteComponent, AnimationSetComponent
from engine.features.sprite.animation import update_animation
from engine.features.physics.components import TransformComponent, VelocityComponent, ColliderComponent
from engine.features.save.logic import SaveManager

from game.features.player.logic import PlayerSystem
from game.features.player.components import PlayerComponent
from game.features.enemy_ai.logic import EnemyAISystem
from game.features.enemy_ai.components import AIComponent
from game.features.npc.logic import NPCSystem
from game.features.npc.components import NPCComponent
from game.features.combat.logic import CombatSystem
from game.features.combat.components import ProjectileComponent
from game.features.inventory.logic import InventorySystem
from game.features.inventory.components import InventoryComponent, DroppedItemComponent
from game.features.character.components import StatsComponent, ClassComponent, NameComponent
from game.features.character.factory import create_player
from game.features.character.renderer import draw_health_bar
from game.features.combat.renderer import draw_projectiles
from game.features.inventory.renderer import draw_dropped_items
from game.features.world_map.logic import WorldMapSystem, load_maps_config
from game.features.world_map.renderer import fill_background
from game.features.shop.renderer import run_shop_menu
from game.features.shop.logic import try_purchase
from game import settings


class GameplayScene(Scene):
    def __init__(self, player_class: str, save_manager: SaveManager,
                 asset_loader, input_state: InputState) -> None:
        self.player_class = player_class
        self.save_manager = save_manager
        self.asset_loader = asset_loader
        self.input_state = input_state
        self.screen: pygame.Surface | None = None
        self.player_entity = None

        # Systems
        self.player_system: PlayerSystem | None = None
        self.enemy_ai_system: EnemyAISystem | None = None
        self.npc_system: NPCSystem | None = None
        self.combat_system: CombatSystem | None = None
        self.inventory_system: InventorySystem | None = None
        self.world_map_system: WorldMapSystem | None = None

        # Camera
        self.camera: CameraState | None = None

        # Tilemaps
        self.tilemap_renderers: dict[str, TilemapRenderer] = {}
        self.tilemap_data: dict[str, TilemapData] = {}
        self.current_map: str = settings.DEFAULT_MAP

        # Timing
        self.last_save_time: float = 0.0
        self.game_over = False

        # Cached images
        self.orb_red_img = None
        self.orb_yellow_img = None
        self.potion_img = None
        self.item_frames: dict[str, list] = {}
        self.font_path: str | None = None

    def on_enter(self) -> None:
        logger.info("Entrée GameplayScene (classe=%s)", self.player_class)
        self.screen = pygame.display.get_surface()
        screen_w, screen_h = self.screen.get_size()
        self.game.settings["screen_size"] = (screen_w, screen_h)

        # Camera
        self.camera = CameraState(screen_w, screen_h)
        self.camera.mode = "center"

        # Load font path
        self.font_path = "assets/fonts/Enchanted_Land.otf"

        # Load projectile images
        for attr, path in [
            ("orb_red_img", "assets/sprites/weapons/orbs/orb_red.png"),
            ("orb_yellow_img", "assets/sprites/weapons/orbs/orb_yellow.png"),
            ("potion_img", "assets/sprites/potions/potion_heal.png"),
        ]:
            try:
                setattr(self, attr, pygame.image.load(path).convert_alpha())
            except (FileNotFoundError, pygame.error) as e:
                logger.warning("Image manquante: %s (%s)", path, e)
                setattr(self, attr, None)

        # Load item frames
        piece_frames = self.asset_loader.load_item_frames("piece")
        if piece_frames:
            self.item_frames["Piece"] = piece_frames

        # Initialize world map system
        self.world_map_system = WorldMapSystem()
        self.world_map_system.game = self.game
        self.game.add_system(self.world_map_system)

        # Load all maps
        maps_config = load_maps_config()
        logger.info("Chargement de %d maps…", len(maps_config))
        for map_name, config in maps_config.items():
            tmx_path = config["tmx_file"]
            tp_defs = self.world_map_system.get_teleporter_defs(map_name)
            collision_layers = config.get("collision_layers", ["Collisions"])

            self.tilemap_data[map_name] = parse_tmx(tmx_path, settings.SCALE,
                                                     collision_layers, tp_defs)
            self.tilemap_renderers[map_name] = TilemapRenderer(tmx_path, settings.SCALE)

        # Determine starting map
        saved_map = self.save_manager.get("map_name")
        if saved_map and saved_map in self.tilemap_data:
            self.current_map = saved_map
        self.world_map_system.current_map = self.current_map

        # Create player entity
        spawn_pos = self.tilemap_data[self.current_map].get_waypoint(settings.DEFAULT_SPAWN)
        if not spawn_pos:
            spawn_pos = (200, 200)

        # Check for saved position
        try:
            saved_pos = self.save_manager.get("player_position")
            if saved_pos and isinstance(saved_pos, dict):
                spawn_pos = (saved_pos["x"], saved_pos["y"])
        except (KeyError, TypeError):
            logger.warning("Position sauvegardée corrompue — position par défaut")

        self.player_entity = create_player(
            self.player_class, settings.PLAYER_NAME,
            spawn_pos[0], spawn_pos[1], self.asset_loader
        )
        self.player_entity.add(PlayerComponent())
        self.player_entity.get(PlayerComponent).current_map = self.current_map

        # Add inventory component
        inventory = InventoryComponent()
        try:
            saved_inv = self.save_manager.get("inventory", [])
            if isinstance(saved_inv, list):
                inventory.items = saved_inv
        except Exception:
            logger.warning("Inventaire sauvegardé corrompu — inventaire vide")
        self.player_entity.add(inventory)

        # Restore saved HP
        stats = self.player_entity.get(StatsComponent)
        try:
            saved_life = self.save_manager.get("player_life")
            if saved_life and isinstance(saved_life, (int, float)) and saved_life > 0:
                stats.hp = int(saved_life)
        except (ValueError, TypeError):
            logger.warning("HP sauvegardés corrompus — HP par défaut")

        # Restore saved stats from player_class
        try:
            saved_class = self.save_manager.get("player_class")
            if saved_class and isinstance(saved_class, dict):
                name_comp = self.player_entity.get(NameComponent)
                if name_comp:
                    name_comp.name = saved_class.get("Name", settings.PLAYER_NAME)
                if "Max HP" in saved_class:
                    stats.max_hp = saved_class["Max HP"]
                if "Attack value" in saved_class:
                    stats.attack = saved_class["Attack value"]
                if "Defend value" in saved_class:
                    stats.defense = saved_class["Defend value"]
                if "Attack range" in saved_class:
                    stats.attack_range = saved_class["Attack range"]
        except (KeyError, TypeError):
            logger.warning("Stats sauvegardées corrompues — stats par défaut")

        self.game.world.add_entity(self.player_entity)
        logger.info("Joueur spawné à (%.0f, %.0f) sur %s", spawn_pos[0], spawn_pos[1], self.current_map)

        # Spawn enemies and NPCs for all maps
        dead_mobs = self.save_manager.get("mob_name", [])
        for map_name, td in self.tilemap_data.items():
            map_size = (td.pixel_width, td.pixel_height)
            self.world_map_system.spawn_enemies_for_map(
                map_name, self.game, self.asset_loader, map_size
            )
            self.world_map_system.spawn_npcs_for_map(
                map_name, self.game, self.asset_loader, td, map_size
            )

        # Remove already killed mobs
        if dead_mobs:
            to_remove = []
            for entity in self.game.world.query(AIComponent, NameComponent):
                name_comp = entity.get(NameComponent)
                if name_comp and name_comp.name in dead_mobs:
                    to_remove.append(entity.id)
            for eid in to_remove:
                self.game.world.remove_entity(eid)

        # Create systems
        self.player_system = PlayerSystem(self.input_state)
        self.player_system.game = self.game
        self.game.add_system(self.player_system)

        self.enemy_ai_system = EnemyAISystem()
        self.enemy_ai_system.game = self.game
        self.game.add_system(self.enemy_ai_system)

        self.npc_system = NPCSystem()
        self.npc_system.game = self.game
        self.game.add_system(self.npc_system)

        self.combat_system = CombatSystem()
        self.combat_system.game = self.game
        self.game.add_system(self.combat_system)

        self.inventory_system = InventorySystem()
        self.inventory_system.game = self.game
        self.game.add_system(self.inventory_system)

        # Subscribe to events
        self.game.event_bus.subscribe("player_died", self._on_player_died)
        self.game.event_bus.subscribe("entity_killed", self._on_entity_killed)

    def _on_player_died(self, entity, **kw) -> None:
        logger.info("Joueur mort — game over")
        self.game_over = True

    def _on_entity_killed(self, entity, name, x, y, map_name, **kw) -> None:
        logger.info("Entité tuée: %s à (%.0f, %.0f) sur %s", name, x, y, map_name)
        # Save dead mob
        dead = self.save_manager.get("mob_name", [])
        if name not in dead:
            dead.append(name)
            self.save_manager.set("mob_name", dead)

    def handle_events(self, events: list) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self._save_and_quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._save_and_quit()

                # Teleport
                if event.key == pygame.K_e:
                    self._try_teleport()

                # Pick up items
                if event.key == pygame.K_a:
                    self._try_pickup()

                # Open shop
                if event.key == pygame.K_r:
                    self._try_open_shop()

                # Use potion
                if event.key == pygame.K_1:
                    self._try_use_potion()

    def update(self, dt: float) -> None:
        if self.game_over:
            return

        # Update all systems
        self.game.update(dt)

        # Update animations for all visible entities on current map
        for entity in self.game.world.query(AnimationSetComponent, SpriteComponent):
            anim = entity.get(AnimationSetComponent)
            sprite = entity.get(SpriteComponent)
            # Only update entities on current map or player
            visible = False
            if entity.has(PlayerComponent):
                visible = True
            elif entity.has(AIComponent):
                ai = entity.get(AIComponent)
                if ai.current_map == self.current_map:
                    visible = True
            elif entity.has(NPCComponent):
                npc = entity.get(NPCComponent)
                if npc.current_map == self.current_map:
                    visible = True
            elif entity.has(ProjectileComponent):
                visible = True

            if visible:
                update_animation(anim, sprite, settings.SCALE)

        # Update feet colliders from current sprite frame
        self._update_feet_colliders()

        # Apply physics integration for entities on current map
        for entity in self.game.world.query(TransformComponent, VelocityComponent):
            if entity.has(ProjectileComponent):
                continue  # handled by CombatSystem
            visible = False
            if entity.has(PlayerComponent):
                visible = True
            elif entity.has(AIComponent) and entity.get(AIComponent).current_map == self.current_map:
                visible = True
            elif entity.has(NPCComponent) and entity.get(NPCComponent).current_map == self.current_map:
                visible = True
            if visible:
                transform = entity.get(TransformComponent)
                velocity = entity.get(VelocityComponent)
                transform.x += velocity.dx * velocity.speed * dt
                transform.y += velocity.dy * velocity.speed * dt

                # Obstacle + map boundary collision
                td = self.tilemap_data.get(self.current_map)
                if td:
                    collider = entity.get(ColliderComponent)
                    if collider and td.collision_rects:
                        # Test X axis separately
                        ex = transform.x + collider.offset_x
                        ey = transform.old_y + collider.offset_y
                        for rect in td.collision_rects:
                            if (ex < rect.x + rect.width and ex + collider.width > rect.x and
                                    ey < rect.y + rect.height and ey + collider.height > rect.y):
                                transform.x = transform.old_x
                                break
                        # Test Y axis separately
                        ex = transform.x + collider.offset_x
                        ey = transform.y + collider.offset_y
                        for rect in td.collision_rects:
                            if (ex < rect.x + rect.width and ex + collider.width > rect.x and
                                    ey < rect.y + rect.height and ey + collider.height > rect.y):
                                transform.y = transform.old_y
                                break

                    # Map boundary clamping (account for collider offset)
                    c_ox = collider.offset_x if collider else 0
                    c_oy = collider.offset_y if collider else 0
                    c_w = collider.width if collider else 0
                    c_h = collider.height if collider else 0
                    if transform.x + c_ox < 0:
                        transform.x = -c_ox
                    if transform.x + c_ox + c_w > td.pixel_width:
                        transform.x = td.pixel_width - c_ox - c_w
                    if transform.y + c_oy < 0:
                        transform.y = -c_oy
                    if transform.y + c_oy + c_h > td.pixel_height:
                        transform.y = td.pixel_height - c_oy - c_h

        # Update camera
        if self.player_entity and self.camera:
            pt = self.player_entity.get(TransformComponent)
            if pt:
                self.camera.update(pt.x, pt.y)

        # Auto-save
        ticks = self.game.time.ticks
        if ticks - self.last_save_time > settings.AUTOSAVE_INTERVAL_MS:
            self._do_save()
            self.last_save_time = ticks

    def render(self) -> None:
        if not self.screen or not self.camera:
            return

        # Background
        bg = self.world_map_system.get_bg_color(self.current_map) if self.world_map_system else "#71ddee"
        fill_background(self.screen, bg)

        # Draw tilemap
        renderer = self.tilemap_renderers.get(self.current_map)
        if renderer:
            renderer.draw(self.screen, self.camera.offset_x, self.camera.offset_y)

        # Collect drawable entities sorted by Y
        drawables = []
        for entity in self.game.world.all_entities():
            sprite = entity.get(SpriteComponent)
            transform = entity.get(TransformComponent)
            if not sprite or not transform or not sprite.visible:
                continue

            # Filter by map
            show = False
            if entity.has(PlayerComponent):
                show = True
            elif entity.has(AIComponent):
                if entity.get(AIComponent).current_map == self.current_map:
                    show = True
            elif entity.has(NPCComponent):
                if entity.get(NPCComponent).current_map == self.current_map:
                    show = True
            elif entity.has(ProjectileComponent):
                show = True
            elif entity.has(DroppedItemComponent):
                if entity.get(DroppedItemComponent).current_map == self.current_map:
                    show = True

            if show and (sprite.image or entity.has(ProjectileComponent) or entity.has(DroppedItemComponent)):
                drawables.append((transform.y, entity, sprite, transform))

        drawables.sort(key=lambda d: d[0])

        ox, oy = self.camera.offset_x, self.camera.offset_y
        for _y, entity, sprite, transform in drawables:
            if entity.has(ProjectileComponent):
                # Draw projectile
                proj = entity.get(ProjectileComponent)
                proj_img = self.orb_yellow_img if proj.is_enemy else self.orb_red_img
                if proj_img is not None:
                    self.screen.blit(proj_img, (transform.x - ox, transform.y - oy))
            elif entity.has(DroppedItemComponent):
                # Draw item
                drop = entity.get(DroppedItemComponent)
                frames = self.item_frames.get(drop.item_name)
                if frames:
                    drop.animation_index += drop.animation_speed
                    if drop.animation_index >= len(frames):
                        drop.animation_index = 0
                    raw = frames[int(drop.animation_index)]
                    w = int(raw.get_width() * settings.SCALE)
                    h = int(raw.get_height() * settings.SCALE)
                    scaled = sprite.get_scaled(w, h)
                    if scaled is None:
                        scaled = pygame.transform.scale(raw, (w, h))
                        sprite.set_scaled(raw, scaled, w, h)
                    self.screen.blit(scaled, (transform.x - ox, transform.y - oy))
            else:
                # Draw character/NPC/enemy
                raw = sprite.image
                if raw:
                    w = int(raw.get_width() * settings.SCALE // 2.5)
                    h = int(raw.get_height() * settings.SCALE // 2.5)
                    scaled = sprite.get_scaled(w, h)
                    if scaled is None:
                        scaled = pygame.transform.scale(raw, (w, h))
                        sprite.set_scaled(raw, scaled, w, h)
                    self.screen.blit(scaled, (transform.x - ox, transform.y - oy))

                # Draw health bar for enemies and player
                if entity.has(AIComponent) or entity.has(PlayerComponent):
                    draw_health_bar(self.screen, entity, ox, oy)

    def _update_feet_colliders(self) -> None:
        """Met à jour le collider pieds depuis l'image sprite courante (s'adapte à chaque frame)."""
        for entity in self.game.world.query(ColliderComponent, SpriteComponent):
            sprite = entity.get(SpriteComponent)
            if not sprite.image:
                continue
            # Utiliser les dimensions cachées si disponibles
            if sprite.image is sprite._cached_raw_ref and sprite._cached_scaled is not None:
                w, h = sprite._cached_w, sprite._cached_h
            else:
                w = int(sprite.image.get_width() * settings.SCALE // 2.5)
                h = int(sprite.image.get_height() * settings.SCALE // 2.5)
            collider = entity.get(ColliderComponent)
            collider.width = w
            collider.height = int(h * 0.2)
            collider.offset_x = 0
            collider.offset_y = int(h * 0.8)

    def _try_teleport(self) -> None:
        if not self.player_entity:
            return
        pt = self.player_entity.get(TransformComponent)
        if not pt:
            return

        td = self.tilemap_data.get(self.current_map)
        if not td:
            return

        for tp in td.teleporters:
            # Check if player is in teleporter zone
            if (tp.x <= pt.x <= tp.x + tp.width and
                    tp.y <= pt.y <= tp.y + tp.height):
                dest_map = tp.destination_map
                dest_wp = tp.destination_waypoint

                if dest_map in self.tilemap_data:
                    dest_pos = self.tilemap_data[dest_map].get_waypoint(dest_wp)
                    if dest_pos:
                        logger.info("Téléport → %s (%s)", dest_map, dest_wp)
                        self.current_map = dest_map
                        if self.world_map_system:
                            self.world_map_system.current_map = dest_map
                        pt.x, pt.y = dest_pos
                        pc = self.player_entity.get(PlayerComponent)
                        if pc:
                            pc.current_map = dest_map
                        return

    def _try_pickup(self) -> None:
        if not self.player_entity:
            return
        pt = self.player_entity.get(TransformComponent)
        inv = self.player_entity.get(InventoryComponent)
        if not pt or not inv:
            return

        to_remove = []
        for entity in self.game.world.query(DroppedItemComponent, TransformComponent):
            drop = entity.get(DroppedItemComponent)
            dt = entity.get(TransformComponent)
            if drop.current_map != self.current_map:
                continue
            dx = pt.x - dt.x
            dy = pt.y - dt.y
            if dx * dx + dy * dy < 50 * 50:
                inv.add_item(drop.item_name)
                to_remove.append(entity.id)
                logger.info("Item ramassé: %s", drop.item_name)

        for eid in to_remove:
            self.game.world.remove_entity(eid)

    def _try_open_shop(self) -> None:
        if not self.player_entity:
            return
        pt = self.player_entity.get(TransformComponent)
        inv = self.player_entity.get(InventoryComponent)
        if not pt or not inv:
            return

        # Check if near a merchant
        for entity in self.game.world.query(NPCComponent, TransformComponent):
            npc = entity.get(NPCComponent)
            nt = entity.get(TransformComponent)
            if npc.npc_type == "Merchant" and npc.current_map == self.current_map:
                dx = pt.x - nt.x
                dy = pt.y - nt.y
                if dx * dx + dy * dy < 100 * 100:
                    logger.info("Ouverture boutique")
                    run_shop_menu(self.screen, inv, self.potion_img, self.font_path)
                    return

    def _try_use_potion(self) -> None:
        if not self.player_entity:
            return
        inv = self.player_entity.get(InventoryComponent)
        stats = self.player_entity.get(StatsComponent)
        if not inv or not stats:
            return

        if inv.count("potion") >= 1:
            inv.remove_item("potion")
            new_hp = int(stats.hp * 1.6)
            stats.hp = min(new_hp, stats.max_hp)
            logger.info("Potion utilisée — HP=%d/%d", stats.hp, stats.max_hp)

    def _do_save(self) -> None:
        if not self.player_entity:
            return
        pt = self.player_entity.get(TransformComponent)
        stats = self.player_entity.get(StatsComponent)
        inv = self.player_entity.get(InventoryComponent)
        class_comp = self.player_entity.get(ClassComponent)
        name_comp = self.player_entity.get(NameComponent)

        if pt:
            self.save_manager.set("player_position", {"x": pt.x, "y": pt.y})
        self.save_manager.set("map_name", self.current_map)
        if stats:
            self.save_manager.set("player_life", stats.hp)
        if inv:
            self.save_manager.set("inventory", inv.items[:])
        if class_comp and stats and name_comp:
            self.save_manager.set("player_class", {
                "Class": class_comp.class_name,
                "Name": name_comp.name,
                "Max HP": stats.max_hp,
                "Attack value": stats.attack,
                "Defend value": stats.defense,
                "Attack range": stats.attack_range,
            })

        self.save_manager.save()
        logger.debug("Auto-save effectué")

    def _save_and_quit(self) -> None:
        logger.info("Sauvegarde et quit")
        self._do_save()
        pygame.quit()
        sys.exit()

    def on_exit(self) -> None:
        self._do_save()
