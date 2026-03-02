from __future__ import annotations
from dataclasses import dataclass
import random


@dataclass
class Combatant:
    name: str
    max_hp: int
    hp: int
    atk: int
    defense: int

    def is_alive(self) -> bool:
        return self.hp > 0


def _damage(attacker_atk: int, defender_def: int) -> int:
    """
    Simple, stable melee damage:
    - always at least 1
    - light randomness
    - defense reduces but doesn't nullify
    """
    base = max(1, attacker_atk - (defender_def // 2))
    roll = random.randint(-1, 2)
    return max(1, base + roll)


class Battle:
    """
    Minimal turn-based battle engine.
    This is intentionally tiny but expandable.
    """
    def __init__(self, player: Combatant, enemy: Combatant) -> None:
        self.player = player
        self.enemy = enemy

        self.turn = "player"  # "player" or "enemy"
        self.log: list[str] = []
        self.over = False
        self.winner: str | None = None

        self.log.append(f"A wild {enemy.name} appeared!")

    def player_melee(self) -> None:
        if self.over or self.turn != "player":
            return
        dmg = _damage(self.player.atk, self.enemy.defense)
        self.enemy.hp = max(0, self.enemy.hp - dmg)
        self.log.append(f"{self.player.name} attacks for {dmg}!")
        if not self.enemy.is_alive():
            self.over = True
            self.winner = "player"
            self.log.append(f"{self.enemy.name} was defeated!")
            return
        self.turn = "enemy"

    def enemy_take_turn(self) -> None:
        if self.over or self.turn != "enemy":
            return
        dmg = _damage(self.enemy.atk, self.player.defense)
        self.player.hp = max(0, self.player.hp - dmg)
        self.log.append(f"{self.enemy.name} hits for {dmg}!")
        if not self.player.is_alive():
            self.over = True
            self.winner = "enemy"
            self.log.append("You were defeated...")
            return
        self.turn = "player"