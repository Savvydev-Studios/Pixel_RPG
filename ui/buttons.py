from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Tuple
import pygame

Color = Tuple[int, int, int]


@dataclass
class ButtonStyle:
    bg: Color = (40, 40, 55)
    bg_hover: Color = (55, 55, 75)
    bg_pressed: Color = (70, 70, 95)
    outline: Color = (110, 110, 140)
    text: Color = (240, 240, 240)
    text_disabled: Color = (150, 150, 150)


class Button:
    """
    Simple button widget.
    - Mouse hover/click
    - Optional keyboard focus + activate()
    """

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        on_click: Callable[[], None],
        *,
        font: pygame.font.Font,
        style: ButtonStyle | None = None,
        enabled: bool = True,
    ) -> None:
        self.rect = rect
        self.text = text
        self.on_click = on_click
        self.font = font
        self.style = style or ButtonStyle()
        self.enabled = enabled

        self.hovered = False
        self.pressed = False
        self.focused = False

    def set_focused(self, focused: bool) -> None:
        self.focused = focused

    def activate(self) -> None:
        if self.enabled:
            self.on_click()

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.enabled:
            return

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                self.on_click()

    def render(self, surface: pygame.Surface) -> None:
        s = self.style

        if not self.enabled:
            bg = s.bg
            text_col = s.text_disabled
        else:
            text_col = s.text
            if self.pressed:
                bg = s.bg_pressed
            elif self.hovered or self.focused:
                bg = s.bg_hover
            else:
                bg = s.bg

        pygame.draw.rect(surface, bg, self.rect, border_radius=10)

        outline_w = 3 if self.focused else 2
        pygame.draw.rect(surface, s.outline, self.rect, width=outline_w, border_radius=10)

        label = self.font.render(self.text, True, text_col)
        surface.blit(label, label.get_rect(center=self.rect.center))