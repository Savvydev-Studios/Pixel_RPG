from __future__ import annotations

import pygame
from constants import TITLE, WIDTH, HEIGHT, FPS, BG_COLOR
from utils import DeltaTime

from screens import ScreenManager, MenuScreen


class Game:
    """
    Step 2: Add a screen system.
    Game owns the loop and delegates input/update/render to the current screen.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.dt_clock = DeltaTime()

        self.running = True

        # Screen system
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

            self.screens.handle_event(event)

    def _update(self, dt: float) -> None:
        self.screens.update(dt)

    def _render(self) -> None:
        self.screen.fill(BG_COLOR)
        self.screens.render(self.screen)
        pygame.display.flip()

    def _shutdown(self) -> None:
        pygame.quit()