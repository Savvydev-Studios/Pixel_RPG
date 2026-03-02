from __future__ import annotations

import pygame
from constants import TITLE, WIDTH, HEIGHT, FPS, BG_COLOR
from utils import DeltaTime

from screens import ScreenManager, MenuScreen


class Game:
    """
    Owns the window + loop.
    Delegates input/update/render to the current screen.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)

        # RESIZABLE window
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.dt_clock = DeltaTime()

        self.running = True

        self.screens = ScreenManager(request_quit=self.stop)
        self.screens.set(MenuScreen())

    def stop(self) -> None:
        self.running = False

    def run(self) -> None:
        while self.running:
            dt = self.dt_clock.tick()
            self._handle_events()
            self._update(dt)
            self._render()
            self.clock.tick(FPS)

        self._shutdown()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # Handle resize at the Game level so the display surface actually changes
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.screens.handle_event(event)

    def _update(self, dt: float) -> None:
        self.screens.update(dt)

    def _render(self) -> None:
        self.screen.fill(BG_COLOR)
        self.screens.render(self.screen)
        pygame.display.flip()

    def _shutdown(self) -> None:
        pygame.quit()