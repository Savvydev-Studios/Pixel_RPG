from __future__ import annotations
from dataclasses import dataclass
import pygame

from systems.controls import Controls


TILE = 32


@dataclass
class Player:
    tx: int
    ty: int
    facing: str = "down"  # "up" | "down" | "left" | "right"


@dataclass
class World:
    tiles: list[list[int]]  # 0=floor, 1=wall

    @property
    def w(self) -> int:
        return len(self.tiles[0]) if self.tiles else 0

    @property
    def h(self) -> int:
        return len(self.tiles)

    def is_blocked(self, tx: int, ty: int) -> bool:
        if tx < 0 or ty < 0 or ty >= self.h or tx >= self.w:
            return True
        return self.tiles[ty][tx] == 1


def make_test_world(w: int = 40, h: int = 26) -> World:
    tiles = [[0 for _ in range(w)] for _ in range(h)]
    for x in range(w):
        tiles[0][x] = 1
        tiles[h - 1][x] = 1
    for y in range(h):
        tiles[y][0] = 1
        tiles[y][w - 1] = 1

    for x in range(6, 18):
        tiles[8][x] = 1
    for y in range(10, 18):
        tiles[y][22] = 1
    for x in range(26, 34):
        tiles[16][x] = 1

    return World(tiles)


class OverworldController:
    """
    Tile movement with hold-to-walk repeat + sprint.
    Still one tile per step. Sprint = faster repeat, not bigger steps.
    """
    def __init__(self, world: World, player: Player) -> None:
        self.world = world
        self.player = player

        self.walk_delay = 0.30
        self.walk_interval = 0.14

        self.sprint_delay = 0.20
        self.sprint_interval = 0.10

        self._held_dir: tuple[int, int] | None = None
        self._timer = 0.0

    def try_move(self, dx: int, dy: int) -> bool:
        nx = self.player.tx + dx
        ny = self.player.ty + dy
        if self.world.is_blocked(nx, ny):
            return False
        self.player.tx = nx
        self.player.ty = ny
        return True

    def _dir_from_keys(self, keys) -> tuple[int, int] | None:
        # Priority: vertical then horizontal (classic RPG feel)
        if Controls.pressed(keys, "move_up"):
            return (0, -1)
        if Controls.pressed(keys, "move_down"):
            return (0, 1)
        if Controls.pressed(keys, "move_left"):
            return (-1, 0)
        if Controls.pressed(keys, "move_right"):
            return (1, 0)
        return None

    def _facing_from_dir(self, d: tuple[int, int]) -> str:
        dx, dy = d
        if dx == 1:
            return "right"
        if dx == -1:
            return "left"
        if dy == -1:
            return "up"
        return "down"

    def update(self, dt: float, keys) -> bool:
        desired = self._dir_from_keys(keys)

        if desired is None:
            self._held_dir = None
            self._timer = 0.0
            return False

        self.player.facing = self._facing_from_dir(desired)

        sprint = Controls.pressed(keys, "sprint")
        delay = self.sprint_delay if sprint else self.walk_delay
        interval = self.sprint_interval if sprint else self.walk_interval

        if desired != self._held_dir:
            self._held_dir = desired
            self._timer = delay
            return self.try_move(*desired)

        self._timer -= dt
        if self._timer > 0:
            return False

        moved = self.try_move(*desired)
        self._timer = interval
        return moved