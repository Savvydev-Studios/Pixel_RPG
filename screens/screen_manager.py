from __future__ import annotations
from typing import Callable, Optional
import pygame

from .base import Screen


class ScreenManager:
    """
    Owns the current screen and handles clean screen switching.
    """

    def __init__(self, request_quit: Callable[[], None]) -> None:
        self._request_quit = request_quit
        self.current: Optional[Screen] = None

    def set(self, screen: Screen) -> None:
        if self.current is not None:
            self.current.on_exit()

        self.current = screen
        self.current.manager = self
        self.current.on_enter()

    def quit(self) -> None:
        self._request_quit()

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current is not None:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current is not None:
            self.current.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if self.current is not None:
            self.current.render(surface)