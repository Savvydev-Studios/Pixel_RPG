from __future__ import annotations
import pygame

from ui import Button, ButtonStyle
from .base import Screen

CLASSES = ["Warrior", "Tank", "Rogue", "Mage", "Ranger", "Cleric", "Berserker", "Assassin"]


class ClassSelectScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.font_title = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)

        self.style = ButtonStyle()
        self.class_index = 0

        self.preview_rect = pygame.Rect(0, 0, 1, 1)
        self.btn_prev: Button | None = None
        self.btn_class: Button | None = None
        self.btn_next: Button | None = None
        self.back_btn: Button | None = None
        self.continue_btn: Button | None = None

    def on_enter(self) -> None:
        self._rebuild_layout()

    def _rebuild_layout(self) -> None:
        surface = pygame.display.get_surface()
        w, h = surface.get_size() if surface else (960, 540)

        panel_w = 620
        x0 = (w // 2) - (panel_w // 2)

        self.preview_rect = pygame.Rect(x0, h // 2 - 110, panel_w, 170)

        picker_y = h // 2 + 80
        arrow_w = 64
        gap = 12
        class_w = panel_w - (arrow_w * 2) - (gap * 2)

        left_rect = pygame.Rect(x0, picker_y, arrow_w, 56)
        class_rect = pygame.Rect(x0 + arrow_w + gap, picker_y, class_w, 56)
        right_rect = pygame.Rect(x0 + arrow_w + gap + class_w + gap, picker_y, arrow_w, 56)

        def prev_class() -> None:
            self.class_index = (self.class_index - 1) % len(CLASSES)

        def next_class() -> None:
            self.class_index = (self.class_index + 1) % len(CLASSES)

        self.btn_prev = Button(left_rect, "<", prev_class, font=self.font, style=self.style)
        self.btn_class = Button(class_rect, CLASSES[self.class_index], lambda: None, font=self.font, style=self.style)
        self.btn_next = Button(right_rect, ">", next_class, font=self.font, style=self.style)

        btn_w = 240
        btn_h = 56
        back_rect = pygame.Rect(x0, picker_y + 86, btn_w, btn_h)
        cont_rect = pygame.Rect(x0 + panel_w - btn_w, picker_y + 86, btn_w, btn_h)

        def go_back() -> None:
            if self.manager:
                from .character_create_screen import CharacterCreateScreen
                self.manager.set(CharacterCreateScreen())

        def go_next() -> None:
            if not self.manager:
                return
            chosen = CLASSES[self.class_index]
            char = self.manager.store.get("character", {})
            char["class"] = chosen
            self.manager.store["character"] = char

            from .overworld_screen import OverworldScreen
            self.manager.set(OverworldScreen())

        self.back_btn = Button(back_rect, "Back", go_back, font=self.font, style=self.style)
        self.continue_btn = Button(cont_rect, "Continue", go_next, font=self.font, style=self.style)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.manager:
                from .character_create_screen import CharacterCreateScreen
                self.manager.set(CharacterCreateScreen())
                return

            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.class_index = (self.class_index - 1) % len(CLASSES)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.class_index = (self.class_index + 1) % len(CLASSES)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.continue_btn:
                self.continue_btn.activate()

        for b in (self.btn_prev, self.btn_class, self.btn_next, self.back_btn, self.continue_btn):
            if b:
                b.handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()

        title = self.font_title.render("Choose Class", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 220)))

        hint = self.font_small.render("← / → to change • Enter to continue • ESC back", True, (200, 200, 200))
        surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 - 185)))

        # Preview panel
        pygame.draw.rect(surface, (28, 28, 40), self.preview_rect, border_radius=18)
        pygame.draw.rect(surface, (105, 105, 140), self.preview_rect, width=2, border_radius=18)

        p_title = self.font_small.render("Preview (placeholder)", True, (200, 200, 200))
        surface.blit(p_title, (self.preview_rect.x + 14, self.preview_rect.y + 12))

        # Placeholder silhouette
        cx = self.preview_rect.centerx
        cy = self.preview_rect.y + 105
        pygame.draw.circle(surface, (180, 180, 200), (cx, cy - 36), 18)
        pygame.draw.rect(surface, (180, 180, 200), pygame.Rect(cx - 12, cy - 16, 24, 52), border_radius=8)

        # Buttons
        if self.btn_class:
            self.btn_class.text = CLASSES[self.class_index]

        for b in (self.btn_prev, self.btn_class, self.btn_next, self.back_btn, self.continue_btn):
            if b:
                b.render(surface)