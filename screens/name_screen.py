from __future__ import annotations
import pygame

from ui import Button, ButtonStyle, TextInput
from .base import Screen


class NameScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.font_title = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.style = ButtonStyle()

        self.name_input: TextInput | None = None
        self.continue_btn: Button | None = None

    def on_enter(self) -> None:
        pygame.key.start_text_input()
        self._rebuild_layout()

    def on_exit(self) -> None:
        pygame.key.stop_text_input()

    def _rebuild_layout(self) -> None:
        surface = pygame.display.get_surface()
        w, h = surface.get_size() if surface else (960, 540)

        panel_w = 520
        x0 = (w // 2) - (panel_w // 2)

        name_rect = pygame.Rect(x0, h // 2 - 10, panel_w, 56)
        self.name_input = TextInput(name_rect, font=self.font, placeholder="Enter name...", max_len=16)
        self.name_input.set_focused(True)

        cont_rect = pygame.Rect(x0, h // 2 + 70, panel_w, 56)

        def go_next() -> None:
            if not self.manager:
                return
            name = (self.name_input.text if self.name_input else "").strip()
            if not name:
                name = "Player"

            char = self.manager.store.get("character", {})
            char["name"] = name
            self.manager.store["character"] = char

            from .character_create_screen import CharacterCreateScreen
            self.manager.set(CharacterCreateScreen())

        self.continue_btn = Button(cont_rect, "Continue", go_next, font=self.font, style=self.style)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.manager:
                from .menu_screen import MenuScreen
                self.manager.set(MenuScreen())
                return

            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.continue_btn:
                self.continue_btn.activate()
                return

        if self.name_input:
            self.name_input.handle_event(event)

        if self.continue_btn:
            self.continue_btn.handle_event(event)

    def render(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()

        title = self.font_title.render("Your Name", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 140)))

        hint = self.font_small.render("Type your name • Enter to continue • ESC back", True, (200, 200, 200))
        surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 - 105)))

        if self.name_input:
            self.name_input.render(surface)

        if self.continue_btn:
            self.continue_btn.render(surface)