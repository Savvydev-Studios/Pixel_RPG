from __future__ import annotations
import pygame
from systems.overworld import TILE, World, Player


def clamp(v: int, lo: int, hi: int) -> int:
    return lo if v < lo else hi if v > hi else v


class Camera:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0

    def update(self, target_px: int, target_py: int, world_px_w: int, world_px_h: int, view_w: int, view_h: int) -> None:
        cx = target_px - view_w // 2
        cy = target_py - view_h // 2
        max_x = max(0, world_px_w - view_w)
        max_y = max(0, world_px_h - view_h)
        self.x = clamp(cx, 0, max_x)
        self.y = clamp(cy, 0, max_y)

    def apply(self, x: int, y: int) -> tuple[int, int]:
        return x - self.x, y - self.y


def draw_world(surface: pygame.Surface, world: World, camera: Camera) -> None:
    w, h = surface.get_size()

    start_tx = max(0, camera.x // TILE)
    start_ty = max(0, camera.y // TILE)
    end_tx = min(world.w, (camera.x + w) // TILE + 2)
    end_ty = min(world.h, (camera.y + h) // TILE + 2)

    floor = (24, 24, 34)
    floor2 = (22, 22, 32)
    wall = (60, 60, 85)
    wall_hi = (75, 75, 105)
    grid = (32, 32, 46)

    for ty in range(start_ty, end_ty):
        for tx in range(start_tx, end_tx):
            x = tx * TILE
            y = ty * TILE
            sx, sy = camera.apply(x, y)

            r = pygame.Rect(sx, sy, TILE, TILE)
            if world.tiles[ty][tx] == 1:
                pygame.draw.rect(surface, wall, r)
                pygame.draw.rect(surface, wall_hi, pygame.Rect(sx, sy, TILE, 4))
            else:
                # subtle checker for depth
                pygame.draw.rect(surface, floor if (tx + ty) % 2 == 0 else floor2, r)

            pygame.draw.rect(surface, grid, r, 1)


def draw_player(surface: pygame.Surface, player: Player, camera: Camera) -> None:
    px = player.tx * TILE + TILE // 2
    py = player.ty * TILE + TILE // 2
    sx, sy = camera.apply(px, py)

    # shadow
    pygame.draw.ellipse(surface, (0, 0, 0), pygame.Rect(sx - 10, sy + 7, 20, 9))

    # palette (placeholder)
    skin = (210, 175, 145)
    hair = (35, 35, 35)
    outfit = (95, 85, 130)
    outline = (18, 18, 26)
    pack = (70, 65, 95)

    # body + head base
    body = pygame.Rect(sx - 7, sy - 1, 14, 14)
    head = pygame.Rect(sx - 6, sy - 13, 12, 12)

    pygame.draw.rect(surface, outline, body.inflate(4, 4), border_radius=6)
    pygame.draw.rect(surface, outfit, body, border_radius=6)

    pygame.draw.ellipse(surface, outline, head.inflate(4, 4))
    pygame.draw.ellipse(surface, skin, head)

    # hair cap
    hair_cap = pygame.Rect(sx - 6, sy - 13, 12, 6)
    pygame.draw.ellipse(surface, hair, hair_cap)

    f = getattr(player, "facing", "down")

    if f == "down":
        # tiny face hint (eyes) on lower half of head
        surface.fill((0, 0, 0), pygame.Rect(sx - 3, sy - 8, 2, 2))
        surface.fill((0, 0, 0), pygame.Rect(sx + 1, sy - 8, 2, 2))
        # small collar/arms hint
        pygame.draw.rect(surface, (120, 110, 160), pygame.Rect(sx - 7, sy + 2, 14, 4), border_radius=3)

    elif f == "up":
        # emphasize backpack straps / back
        pygame.draw.rect(surface, pack, pygame.Rect(sx - 8, sy + 1, 16, 6), border_radius=4)
        pygame.draw.rect(surface, outline, pygame.Rect(sx - 8, sy + 1, 16, 6), width=2, border_radius=4)

    elif f == "left":
        # side profile: shift “face” dot left
        surface.fill((0, 0, 0), pygame.Rect(sx - 4, sy - 9, 2, 2))
        # shoulder hint to left
        pygame.draw.rect(surface, (120, 110, 160), pygame.Rect(sx - 8, sy + 2, 6, 4), border_radius=3)

    elif f == "right":
        surface.fill((0, 0, 0), pygame.Rect(sx + 2, sy - 9, 2, 2))
        pygame.draw.rect(surface, (120, 110, 160), pygame.Rect(sx + 2, sy + 2, 6, 4), border_radius=3)