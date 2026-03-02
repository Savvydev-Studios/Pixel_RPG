from __future__ import annotations
import pygame

from .base import Screen
from ui import Button, ButtonStyle
from ui.style import Fonts
from systems.battle import Battle, Combatant


class BattleScreen(Screen):
    """
    Minimal battle screen:
    - Melee button only (for now)
    - Enemy auto-attacks after player
    - Log + HP bars
    - ESC returns to menu (for now)
    """
    def __init__(self) -> None:
        super().__init__()
        self.font_title = Fonts.title()
        self.font = Fonts.ui()
        self.font_small = Fonts.small()
        self.style = ButtonStyle()

        self.container = pygame.Rect(0, 0, 1, 1)
        self.log_rect = pygame.Rect(0, 0, 1, 1)
        self.player_panel = pygame.Rect(0, 0, 1, 1)
        self.enemy_panel = pygame.Rect(0, 0, 1, 1)

        self.btn_melee: Button | None = None
        self.btn_back: Button | None = None

        self.battle: Battle | None = None
        self._pending_enemy = False
        self._enemy_timer = 0.0

    def on_enter(self) -> None:
        # Temporary test combatants.
        # Later we’ll build these from player + encounters system.
        player = Combatant(name="Hero", max_hp=30, hp=30, atk=8, defense=4)
        enemy = Combatant(name="Slime", max_hp=22, hp=22, atk=6, defense=2)
        self.battle = Battle(player, enemy)

        self._rebuild_layout()

    def _rebuild_layout(self) -> None:
        surf = pygame.display.get_surface()
        w, h = surf.get_size() if surf else (1400, 800)

        cw = min(1100, w - 80)
        ch = min(640, h - 80)
        self.container = pygame.Rect((w - cw) // 2, (h - ch) // 2, cw, ch)

        pad = 18
        top = self.container.y + pad
        left = self.container.x + pad

        # panels
        panel_h = 160
        self.enemy_panel = pygame.Rect(left, top, self.container.w - pad * 2, panel_h)

        self.player_panel = pygame.Rect(left, self.enemy_panel.bottom + 14, self.container.w - pad * 2, panel_h)

        # log
        self.log_rect = pygame.Rect(left, self.player_panel.bottom + 14, self.container.w - pad * 2, 160)

        # buttons
        btn_h = 52
        btn_w = 220
        by = self.container.bottom - pad - btn_h

        self.btn_back = Button(
            pygame.Rect(self.container.x + pad, by, btn_w, btn_h),
            "Back",
            self._go_back,
            font=self.font,
            style=self.style,
        )

        self.btn_melee = Button(
            pygame.Rect(self.container.right - pad - btn_w, by, btn_w, btn_h),
            "Melee",
            self._melee,
            font=self.font,
            style=self.style,
        )

    def _go_back(self) -> None:
        # For now, return to menu.
        if self.manager:
            from .menu_screen import MenuScreen
            self.manager.set(MenuScreen())

    def _melee(self) -> None:
        if not self.battle:
            return
        self.battle.player_melee()
        if self.battle.turn == "enemy" and not self.battle.over:
            self._pending_enemy = True
            self._enemy_timer = 0.35  # small delay so it feels turn-based, not instant

    def update(self, dt: float) -> None:
        if not self.battle:
            return
        if self._pending_enemy:
            self._enemy_timer -= dt
            if self._enemy_timer <= 0:
                self._pending_enemy = False
                self.battle.enemy_take_turn()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_back()
            return

        if event.type == pygame.VIDEORESIZE:
            self._rebuild_layout()
            return

        if self.btn_back:
            self.btn_back.handle_event(event)

        # disable input when it’s enemy turn or battle over
        if self.battle and (self.battle.turn != "player" or self.battle.over):
            return

        if self.btn_melee:
            self.btn_melee.handle_event(event)

    def _draw_panel(self, surface: pygame.Surface, rect: pygame.Rect, title: str) -> None:
        pygame.draw.rect(surface, (28, 28, 40), rect, border_radius=16)
        pygame.draw.rect(surface, (105, 105, 140), rect, width=2, border_radius=16)

        t = self.font_small.render(title, True, (220, 220, 220))
        surface.blit(t, (rect.x + 14, rect.y + 10))

    def _draw_hp_bar(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, hp: int, max_hp: int) -> None:
        pygame.draw.rect(surface, (18, 18, 26), pygame.Rect(x, y, w, h), border_radius=8)
        pct = 0 if max_hp <= 0 else max(0, min(1, hp / max_hp))
        fill_w = int(w * pct)
        pygame.draw.rect(surface, (70, 170, 110), pygame.Rect(x, y, fill_w, h), border_radius=8)
        pygame.draw.rect(surface, (105, 105, 140), pygame.Rect(x, y, w, h), width=2, border_radius=8)

        txt = self.font_small.render(f"{hp}/{max_hp}", True, (240, 240, 240))
        surface.blit(txt, txt.get_rect(center=(x + w // 2, y + h // 2)))

    def _draw_log(self, surface: pygame.Surface) -> None:
        rect = self.log_rect
        pygame.draw.rect(surface, (28, 28, 40), rect, border_radius=16)
        pygame.draw.rect(surface, (105, 105, 140), rect, width=2, border_radius=16)

        title = self.font_small.render("Battle Log", True, (220, 220, 220))
        surface.blit(title, (rect.x + 14, rect.y + 10))

        if not self.battle:
            return

        # last 5 lines
        lines = self.battle.log[-5:]
        y = rect.y + 38
        for line in lines:
            img = self.font_small.render(line, True, (240, 240, 240))
            surface.blit(img, (rect.x + 14, y))
            y += 24

        if self.battle.over:
            msg = "Victory!" if self.battle.winner == "player" else "Defeat..."
            img = self.font.render(msg, True, (245, 245, 245))
            surface.blit(img, img.get_rect(midright=(rect.right - 14, rect.y + 22)))

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (18, 18, 26), self.container, border_radius=18)
        pygame.draw.rect(surface, (105, 105, 140), self.container, width=2, border_radius=18)

        title = self.font_title.render("Battle", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(self.container.centerx, self.container.y - 26)))

        # panels
        self._draw_panel(surface, self.enemy_panel, "Enemy")
        self._draw_panel(surface, self.player_panel, "Player")

        if self.battle:
            # enemy info
            e = self.battle.enemy
            p = self.battle.player

            en = self.font.render(e.name, True, (240, 240, 240))
            surface.blit(en, (self.enemy_panel.x + 14, self.enemy_panel.y + 44))
            self._draw_hp_bar(surface, self.enemy_panel.x + 14, self.enemy_panel.y + 84, 240, 22, e.hp, e.max_hp)

            pn = self.font.render(p.name, True, (240, 240, 240))
            surface.blit(pn, (self.player_panel.x + 14, self.player_panel.y + 44))
            self._draw_hp_bar(surface, self.player_panel.x + 14, self.player_panel.y + 84, 240, 22, p.hp, p.max_hp)

            # turn indicator
            turn = "Your Turn" if self.battle.turn == "player" else "Enemy Turn"
            ti = self.font_small.render(turn, True, (220, 220, 220))
            surface.blit(ti, (self.player_panel.right - 140, self.player_panel.y + 14))

        self._draw_log(surface)

        if self.btn_back:
            self.btn_back.render(surface)

        if self.btn_melee:
            # dim button if not player's turn
            if self.battle and (self.battle.turn != "player" or self.battle.over):
                # cheap “disabled” overlay
                self.btn_melee.render(surface)
                r = self.btn_melee.rect
                overlay = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                surface.blit(overlay, r.topleft)
            else:
                self.btn_melee.render(surface)