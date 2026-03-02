from __future__ import annotations
import pygame

from constants import DEV_MODE
from systems.controls import Controls
from ui.dev_menu import DevDropdownMenu


class ScreenManager:
    def __init__(self, request_quit=None) -> None:
        self.current = None
        self.running = True
        self.store: dict = {}

        self._request_quit = request_quit

        self._dev_menu = DevDropdownMenu()
        self._dev_items_built = False

    def set(self, screen) -> None:
        self.current = screen
        self.current.manager = self
        self.current.on_enter()
        self._dev_items_built = False

    def quit(self) -> None:
        if callable(self._request_quit):
            self._request_quit()
        else:
            self.running = False

    def _build_dev_items(self) -> None:
        if self._dev_items_built:
            return
        self._dev_items_built = True

        def go_menu():
            from screens.menu_screen import MenuScreen
            self.set(MenuScreen())

        def go_overworld():
            from screens.overworld_screen import OverworldScreen
            self.set(OverworldScreen())

        def go_name():
            from screens.name_screen import NameScreen
            self.set(NameScreen())

        def go_designer():
            from screens.character_create_screen import CharacterCreateScreen
            self.set(CharacterCreateScreen())

        def go_class():
            from screens.class_select_screen import ClassSelectScreen
            self.set(ClassSelectScreen())

        def go_battle():
            from screens.battle_screen import BattleScreen
            self.set(BattleScreen())

        def go_message():
            from screens.message_screen import MessageScreen
            self.set(MessageScreen("Dev", "Hello from Dev Mode."))

        def dump_store():
            from screens.message_screen import MessageScreen
            txt = "\n".join([f"{k}: {v}" for k, v in self.store.items()]) or "(store empty)"
            self.set(MessageScreen("Dev Store", txt))

        self._dev_menu.set_items([
            ("Go: Menu", go_menu),
            ("Go: Overworld", go_overworld),
            ("Go: Name Screen", go_name),
            ("Go: Character Designer", go_designer),
            ("Go: Class Select", go_class),
            ("Go: Battle Screen", go_battle),
            ("Show: Dev Message", go_message),
            ("Debug: View store", dump_store),
        ])

    def handle_event(self, event: pygame.event.Event) -> None:
        if DEV_MODE:
            if Controls.keydown(event, "dev_menu"):
                self._build_dev_items()
                self._dev_menu.toggle()
                return

            if self._dev_menu.visible:
                self._dev_menu.handle_event(event)
                return

        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if self.current:
            self.current.render(surface)

        if DEV_MODE:
            self._dev_menu.render(surface)