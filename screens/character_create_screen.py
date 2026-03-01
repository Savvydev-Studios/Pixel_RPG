from __future__ import annotations
import pygame

from ui import Button, ButtonStyle
from .base import Screen


class CharacterCreateScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.font_title = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)

        self.style = ButtonStyle()
        self.continue_btn: Button | None = None
        self.back_btn: Button | None = None

        self.panel_rect = pygame.Rect(0, 0, 1, 1)

    def on_enter(self) -> None:
        self._rebuild_layout()

    def _rebuild_layout(self) -> None:
        surface = pygame.display.get_surface()
        w, h = surface.get_size() if surface else (960, 540)

        panel_w = 700
        panel_h = 320
        self.panel_rect = pygame.Rect((w // 2) - (panel_w // 2), (h // 2) - (panel_h // 2) + 10, panel_w, panel_h)

        btn_w = 240
        btn_h = 56
        gap = 14

        back_rect = pygame.Rect(self.panel_rect.x, self.panel_rect.bottom + 24, btn_w, btn_h)
        cont_rect = pygame.Rect(self.panel_rect.right - btn_w, self.panel_rect.bottom + 24, btn_w, btn_h)

        def go_back() -> None:
            if self.manager:
                from .name_screen import NameScreen
                self.manager.set(NameScreen())

        def go_next() -> None:
            if self.manager:
                from .class_select_screen import ClassSelectScreen
                self.manager.set(ClassSelectScreen())

        self.back_btn = Button(back_rect, "Back", go_back, font=self.font, style=self.style)
        self.continue_btn = Button(cont_rect, "Continue", go_next, font=self.font, style=self.style)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.manager:
                from .name_screen import NameScreen
                self.manager.set(NameScreen())
                return

            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.continue_btn:
                self.continue_btn.activate()
                return

        if self.back_btn:
            self.back_btn.handle_event(event)
        if self.continue_btn:
            self.continue_btn.handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()

        title = self.font_title.render("Character Designer", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 220)))

        hint = self.font_small.render("Next step: gender, skin, hair, eyes, style + live preview", True, (200, 200, 200))
        surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 - 185)))

        # Big reserved workspace panel
        pygame.draw.rect(surface, (28, 28, 40), self.panel_rect, border_radius=18)
        pygame.draw.rect(surface, (105, 105, 140), self.panel_rect, width=2, border_radius=18)

        # Placeholder layout guides so it already feels structured
        left = pygame.Rect(self.panel_rect.x + 18, self.panel_rect.y + 18, self.panel_rect.w * 0.55, self.panel_rect.h - 36)
        right = pygame.Rect(left.right + 18, left.y, self.panel_rect.right - (left.right + 36), left.h)

        pygame.draw.rect(surface, (22, 22, 32), left, border_radius=14)
        pygame.draw.rect(surface, (22, 22, 32), right, border_radius=14)

        surface.blit(self.font_small.render("Controls (placeholder)", True, (200, 200, 200)), (left.x + 14, left.y + 12))
        surface.blit(self.font_small.render("Preview (placeholder)", True, (200, 200, 200)), (right.x + 14, right.y + 12))

        # Simple silhouette preview placeholder
        cx = right.centerx
        cy = right.y + 170
        pygame.draw.circle(surface, (180, 180, 200), (cx, cy - 45), 18)
        pygame.draw.rect(surface, (180, 180, 200), pygame.Rect(cx - 12, cy - 25, 24, 50), border_radius=8)

        if self.back_btn:
            self.back_btn.render(surface)
        if self.continue_btn:
            self.continue_btn.render(surface)