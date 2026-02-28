from __future__ import annotations
from typing import Optional
import pygame


class Screen:
    """
    Base class for all screens (menu, overworld, battle, etc).
    Screens are stateful and own their own input/update/render.
    """

    def __init__(self) -> None:
        self.manager: Optional["ScreenManager"] = None  # set by ScreenManager

    def on_enter(self) -> None:
        """Called when this screen becomes active."""
        pass

    def on_exit(self) -> None:
        """Called when this screen stops being active."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass