from __future__ import annotations
import pygame

from .base import Screen


class MessageScreen(Screen):
    def __init__(self, title: str, message: str) -> None:
        super().__init__()
        self.title_text = title
        self.message_text = message
        self.font_title = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 28)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.manager:
            from .menu_screen import MenuScreen
            self.manager.set(MenuScreen())

    def render(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()

        title = self.font_title.render(self.title_text, True, (240, 240, 240))
        msg = self.font.render(self.message_text, True, (200, 200, 200))
        hint = self.font.render("ESC to return", True, (200, 200, 200))

        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 50)))
        surface.blit(msg, msg.get_rect(center=(w // 2, h // 2)))
        surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 50)))