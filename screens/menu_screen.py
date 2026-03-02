from __future__ import annotations
import pygame

from constants import TITLE
from ui import Button, ButtonStyle
from ui.style import Fonts
from systems.controls import Controls
from .base import Screen
from .message_screen import MessageScreen


class MenuScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.font_title = Fonts.title()
        self.font = Fonts.ui()

        self.buttons: list[Button] = []
        self.focus_index = 0
        self.style = ButtonStyle()

    def on_enter(self) -> None:
        self._rebuild_layout()

    def _rebuild_layout(self) -> None:
        surface = pygame.display.get_surface()
        w, h = surface.get_size() if surface else (960, 540)

        btn_w = 320
        btn_h = 56
        gap = 14

        total_h = (btn_h * 3) + (gap * 2)
        start_y = (h // 2) - (total_h // 2) + 30
        x = (w // 2) - (btn_w // 2)

        def go_new() -> None:
            if self.manager:
                from .character_create_screen import CharacterCreateScreen
                self.manager.set(CharacterCreateScreen())

        def go_load() -> None:
            if self.manager:
                self.manager.set(MessageScreen("Load Game", "Save system comes later."))

        def go_quit() -> None:
            if self.manager:
                self.manager.quit()

        self.buttons = [
            Button(pygame.Rect(x, start_y + (btn_h + gap) * 0, btn_w, btn_h), "New Game", go_new, font=self.font, style=self.style),
            Button(pygame.Rect(x, start_y + (btn_h + gap) * 1, btn_w, btn_h), "Load Game", go_load, font=self.font, style=self.style),
            Button(pygame.Rect(x, start_y + (btn_h + gap) * 2, btn_w, btn_h), "Quit", go_quit, font=self.font, style=self.style),
        ]

        self.focus_index = 0
        self._apply_focus()

    def _apply_focus(self) -> None:
        for i, b in enumerate(self.buttons):
            b.set_focused(i == self.focus_index)

    def handle_event(self, event: pygame.event.Event) -> None:
        for b in self.buttons:
            b.handle_event(event)

        if Controls.keydown(event, "cancel") and self.manager:
            self.manager.quit()
            return

        if Controls.keydown(event, "move_up"):
            self.focus_index = (self.focus_index - 1) % len(self.buttons)
            self._apply_focus()
            return

        if Controls.keydown(event, "move_down"):
            self.focus_index = (self.focus_index + 1) % len(self.buttons)
            self._apply_focus()
            return

        if Controls.keydown(event, "confirm"):
            self.buttons[self.focus_index].activate()
            return

    def render(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()

        title = self.font_title.render(TITLE, True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 140)))

        for b in self.buttons:
            b.render(surface)