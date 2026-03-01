from __future__ import annotations
import pygame
import time


class TextInput:
    """
    Minimal text input widget.
    - Click to focus
    - Type characters
    - Backspace deletes
    - Blinking caret when focused
    """

    def __init__(
        self,
        rect: pygame.Rect,
        *,
        font: pygame.font.Font,
        placeholder: str = "",
        max_len: int = 16,
    ) -> None:
        self.rect = rect
        self.font = font
        self.placeholder = placeholder
        self.max_len = max_len

        self.text = ""
        self.focused = False

        # caret
        self._caret_visible = True
        self._last_blink = time.time()
        self._blink_interval = 0.5

    def set_focused(self, focused: bool) -> None:
        self.focused = focused
        if focused:
            self._caret_visible = True
            self._last_blink = time.time()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.rect.collidepoint(event.pos)

        if not self.focused:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

        elif event.type == pygame.TEXTINPUT:
            if len(self.text) < self.max_len:
                ch = event.text
                if ch and ch not in ("\n", "\r"):
                    self.text += ch

    def _update_caret(self) -> None:
        if not self.focused:
            return

        now = time.time()
        if now - self._last_blink >= self._blink_interval:
            self._caret_visible = not self._caret_visible
            self._last_blink = now

    def render(self, surface: pygame.Surface) -> None:
        self._update_caret()

        # background + outline
        if self.focused:
            bg = (48, 48, 66)
            outline = (160, 160, 210)
        else:
            bg = (35, 35, 50)
            outline = (105, 105, 140)

        pygame.draw.rect(surface, bg, self.rect, border_radius=10)
        pygame.draw.rect(surface, outline, self.rect, width=2, border_radius=10)

        display_text = self.text

        # blinking caret
        if self.focused and self._caret_visible:
            display_text += "|"

        if display_text:
            label = self.font.render(display_text, True, (240, 240, 240))
        else:
            label = self.font.render(self.placeholder, True, (150, 150, 150))

        surface.blit(label, label.get_rect(midleft=(self.rect.x + 14, self.rect.centery)))