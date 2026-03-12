"""DebugOverlay: debug visuel cyclique (F3) — texte, hitboxes, vélocité, stats."""

import pygame

from engine.features.physics.components import (
    TransformComponent, VelocityComponent, ColliderComponent,
)
from engine.features.sprite.components import SpriteComponent
from game.features.player.components import PlayerComponent
from game.features.enemy_ai.components import AIComponent
from game.features.npc.components import NPCComponent
from game.features.combat.components import ProjectileComponent
from game.features.inventory.components import DroppedItemComponent
from game.features.character.components import StatsComponent
from game import settings


# Debug levels: 0=OFF, 1=TEXT, 2=VISUAL, 3=ALL
_LEVEL_NAMES = {0: "OFF", 1: "TEXT", 2: "VISUAL", 3: "ALL"}
_MAX_LEVEL = 3


class DebugOverlay:
    def __init__(self) -> None:
        self.level: int = 0
        self._clock: pygame.time.Clock | None = None
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None
        # Cache collision surfaces per map
        self._collision_cache: dict[str, pygame.Surface] = {}
        self._collision_cache_map: str | None = None

    def init(self, clock: pygame.time.Clock) -> None:
        self._clock = clock
        self._font = pygame.font.SysFont("monospace", 18)
        self._small_font = pygame.font.SysFont("monospace", 14)

    def cycle(self) -> None:
        self.level = (self.level + 1) % (_MAX_LEVEL + 1)

    # ------------------------------------------------------------------
    # Main render dispatch
    # ------------------------------------------------------------------
    def render(self, screen: pygame.Surface, world, current_map: str,
               camera_offset: tuple[float, float] = (0.0, 0.0),
               tilemap_data=None) -> None:
        if self.level == 0 or not self._font:
            return

        if self.level in (1, 3):
            self._render_text(screen, world, current_map)
        if self.level in (2, 3):
            self._render_visual(screen, world, current_map, camera_offset, tilemap_data)

    # ------------------------------------------------------------------
    # Level 1 — Text overlay
    # ------------------------------------------------------------------
    def _render_text(self, screen: pygame.Surface, world, current_map: str) -> None:
        fps = self._clock.get_fps() if self._clock else 0.0
        entity_count = len(world)

        player_pos = "N/A"
        for entity in world.query(PlayerComponent, TransformComponent):
            t = entity.get(TransformComponent)
            player_pos = f"{t.x:.0f}, {t.y:.0f}"
            break

        level_label = f"[{self.level}/{_MAX_LEVEL}] {_LEVEL_NAMES[self.level]}"
        lines = [
            level_label,
            f"FPS: {fps:.0f}",
            f"Entités: {entity_count}",
            f"Position: {player_pos}",
            f"Map: {current_map}",
        ]

        padding = 6
        line_h = 20
        box_w = 260
        box_h = padding * 2 + line_h * len(lines)

        overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (8, 8))

        for i, line in enumerate(lines):
            surf = self._font.render(line, True, (0, 255, 0))
            screen.blit(surf, (8 + padding, 8 + padding + i * line_h))

    # ------------------------------------------------------------------
    # Level 2 — Visual debug
    # ------------------------------------------------------------------
    def _render_visual(self, screen: pygame.Surface, world, current_map: str,
                       camera_offset: tuple[float, float],
                       tilemap_data) -> None:
        ox, oy = camera_offset

        # 1. Collision rects tilemap (cached surface)
        if tilemap_data and current_map in tilemap_data:
            td = tilemap_data[current_map]
            self._draw_collision_rects(screen, td, current_map, ox, oy)

            # 3. Teleporter zones
            for tp in td.teleporters:
                tp_surf = pygame.Surface((int(tp.width), int(tp.height)), pygame.SRCALPHA)
                tp_surf.fill((180, 0, 255, 80))
                screen.blit(tp_surf, (tp.x - ox, tp.y - oy))
                if self._small_font:
                    label = self._small_font.render(
                        f"→ {tp.destination_map}", True, (220, 180, 255)
                    )
                    screen.blit(label, (tp.x - ox + 2, tp.y - oy - 14))

            # 3b. Waypoints (coordonnées TMX × scale)
            s = settings.SCALE
            for wp in td.waypoints:
                wx, wy = int(wp.x * s - ox), int(wp.y * s - oy)
                pygame.draw.circle(screen, (255, 255, 0), (wx, wy), 5, 1)
                pygame.draw.line(screen, (255, 255, 0), (wx - 7, wy), (wx + 7, wy), 1)
                pygame.draw.line(screen, (255, 255, 0), (wx, wy - 7), (wx, wy + 7), 1)
                if self._small_font:
                    label = self._small_font.render(wp.name, True, (255, 255, 0))
                    screen.blit(label, (wx + 8, wy - 7))

        # 2. Entity hitboxes + 4. velocity vectors + 5. stats
        for entity in world.query(ColliderComponent, TransformComponent):
            collider = entity.get(ColliderComponent)
            transform = entity.get(TransformComponent)

            # Determine color by entity type
            if entity.has(PlayerComponent):
                color = (0, 255, 0)
            elif entity.has(AIComponent):
                color = (255, 0, 0)
            elif entity.has(NPCComponent):
                color = (0, 100, 255)
            elif entity.has(ProjectileComponent):
                color = (255, 255, 0)
            else:
                color = (200, 200, 200)

            # Filter by current map (skip off-map entities)
            if entity.has(AIComponent):
                if entity.get(AIComponent).current_map != current_map:
                    continue
            elif entity.has(NPCComponent):
                if entity.get(NPCComponent).current_map != current_map:
                    continue

            # Draw hitbox rect (collider)
            rect_x = collider.left - ox
            rect_y = collider.top - oy
            pygame.draw.rect(screen, color,
                             (rect_x, rect_y, collider.width, collider.height), 2)

            # Draw sprite image rect (magenta)
            self._draw_sprite_rect(screen, entity, transform, ox, oy)

            # 4. Velocity vector
            vel = entity.get(VelocityComponent) if entity.has(VelocityComponent) else None
            if vel and (vel.dx != 0 or vel.dy != 0):
                cx = transform.x + collider.offset_x + collider.width / 2 - ox
                cy = transform.y + collider.offset_y + collider.height / 2 - oy
                mag = vel.magnitude
                length = min(mag * 50, 200)
                if mag > 0:
                    end_x = cx + (vel.dx / mag) * length
                    end_y = cy + (vel.dy / mag) * length
                    pygame.draw.line(screen, (0, 255, 255),
                                     (int(cx), int(cy)), (int(end_x), int(end_y)), 2)

            # 5. Stats label (skip projectiles)
            if not entity.has(ProjectileComponent) and self._small_font:
                stats = entity.get(StatsComponent) if entity.has(StatsComponent) else None
                if stats:
                    label = f"#{entity.id} HP:{stats.hp}/{stats.max_hp} ATK:{stats.attack} DEF:{stats.defense}"
                    surf = self._small_font.render(label, True, (255, 255, 255))
                    screen.blit(surf, (transform.x - ox, transform.y - oy - 16))

        # 6. Sprite-only entities (no collider) — projectiles, dropped items
        for entity in world.query(TransformComponent, SpriteComponent):
            if entity.has(ColliderComponent):
                continue  # already handled above
            transform = entity.get(TransformComponent)
            self._draw_sprite_rect(screen, entity, transform, ox, oy)

        # 7. Interaction zones — NPC merchants (rayon 100)
        for entity in world.query(NPCComponent, TransformComponent, SpriteComponent):
            npc = entity.get(NPCComponent)
            if npc.current_map != current_map:
                continue
            if npc.npc_type == "Merchant":
                t = entity.get(TransformComponent)
                sprite = entity.get(SpriteComponent)
                if sprite and sprite._cached_scaled:
                    cx = int(t.x + sprite._cached_w / 2 - ox)
                    cy = int(t.y + sprite._cached_h / 2 - oy)
                else:
                    cx, cy = int(t.x - ox), int(t.y - oy)
                pygame.draw.circle(screen, (255, 165, 0), (cx, cy), 100, 1)
                if self._small_font:
                    label = self._small_font.render("Shop (R)", True, (255, 165, 0))
                    screen.blit(label, (cx - label.get_width() // 2, cy - 110))

        # 8. Interaction zones — dropped items (rayon 50)
        for entity in world.query(DroppedItemComponent, TransformComponent):
            drop = entity.get(DroppedItemComponent)
            if drop.current_map != current_map:
                continue
            t = entity.get(TransformComponent)
            sprite = entity.get(SpriteComponent) if entity.has(SpriteComponent) else None
            if sprite and sprite._cached_scaled:
                cx = int(t.x + sprite._cached_w / 2 - ox)
                cy = int(t.y + sprite._cached_h / 2 - oy)
            else:
                cx, cy = int(t.x - ox), int(t.y - oy)
            pygame.draw.circle(screen, (0, 200, 200), (cx, cy), 50, 1)
            if self._small_font:
                label = self._small_font.render("Pickup (A)", True, (0, 200, 200))
                screen.blit(label, (cx - label.get_width() // 2, cy - 60))

        # 9. Player interaction points
        for entity in world.query(PlayerComponent, TransformComponent, SpriteComponent):
            t = entity.get(TransformComponent)
            sprite = entity.get(SpriteComponent)
            collider = entity.get(ColliderComponent) if entity.has(ColliderComponent) else None
            # Centre image (blanc) — interactions NPC/items
            if sprite and sprite._cached_scaled:
                cx = int(t.x + sprite._cached_w / 2 - ox)
                cy = int(t.y + sprite._cached_h / 2 - oy)
            else:
                cx, cy = int(t.x - ox), int(t.y - oy)
            pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 3)
            # Centre pieds (rouge) — téléportation
            if collider and collider.width > 0:
                fx = int(t.x + collider.offset_x + collider.width / 2 - ox)
                fy = int(t.y + collider.offset_y + collider.height / 2 - oy)
                pygame.draw.circle(screen, (255, 0, 0), (fx, fy), 3)

    # ------------------------------------------------------------------
    # Sprite image rect
    # ------------------------------------------------------------------
    def _draw_sprite_rect(self, screen: pygame.Surface, entity, transform,
                          ox: float, oy: float) -> None:
        """Draw magenta outline for the rendered sprite image bounds."""
        sprite = entity.get(SpriteComponent) if entity.has(SpriteComponent) else None
        if sprite and sprite.image:
            img = sprite.image
            if entity.has(ProjectileComponent):
                w, h = img.get_width(), img.get_height()
            elif entity.has(DroppedItemComponent):
                w = int(img.get_width() * settings.SCALE)
                h = int(img.get_height() * settings.SCALE)
            else:
                w = int(img.get_width() * settings.SCALE // 2.5)
                h = int(img.get_height() * settings.SCALE // 2.5)
            pygame.draw.rect(screen, (255, 0, 255),
                             (transform.x - ox, transform.y - oy, w, h), 1)

    # ------------------------------------------------------------------
    # Collision rects cache
    # ------------------------------------------------------------------
    def _draw_collision_rects(self, screen: pygame.Surface, td, current_map: str,
                              ox: float, oy: float) -> None:
        if current_map != self._collision_cache_map or current_map not in self._collision_cache:
            # Build cached surface
            surf = pygame.Surface((td.pixel_width, td.pixel_height), pygame.SRCALPHA)
            for rect in td.collision_rects:
                pygame.draw.rect(surf, (255, 0, 0, 60),
                                 (int(rect.x), int(rect.y), int(rect.width), int(rect.height)))
            self._collision_cache[current_map] = surf
            self._collision_cache_map = current_map

        screen.blit(self._collision_cache[current_map], (-ox, -oy))
