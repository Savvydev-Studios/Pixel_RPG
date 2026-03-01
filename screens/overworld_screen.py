from __future__ import annotations
import pygame

from .base import Screen


class OverworldScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.font_title = pygame.font.Font(None, 54)
        self.font = pygame.font.Font(None, 28)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.manager:
            from .menu_screen import MenuScreen
            self.manager.set(MenuScreen())

    def render(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()

        title = self.font_title.render("Overworld (placeholder)", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 40)))

        name = "?"
        cls = "?"
        if self.manager and "character" in self.manager.store:
            data = self.manager.store["character"]
            name = str(data.get("name", "?"))
            cls = str(data.get("class", "?"))

        info = self.font.render(f"Character: {name}  |  Class: {cls}", True, (200, 200, 200))
        surface.blit(info, info.get_rect(center=(w // 2, h // 2 + 20)))

        hint = self.font.render("ESC to return to menu", True, (200, 200, 200))
        surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 70)))