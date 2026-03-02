from __future__ import annotations
import pygame
from ui.style import Fonts


class DevDropdownMenu:
    """
    Small dev dropdown that renders over the current screen.
    - Visible only when DEV_MODE True (controlled by caller)
    - Toggle visibility with F1 (handled by caller)
    - Scrollable list (mouse wheel / up/down)
    """

    def __init__(self) -> None:
        self.visible = False
        self.items: list[tuple[str, callable]] = []
        self.scroll = 0
        self.selected = 0
        self.max_visible = 6

        self.font = Fonts.small()
        self.font_title = Fonts.small()

        # layout (computed each render)
        self.panel = pygame.Rect(0, 0, 1, 1)
        self.item_rects: list[pygame.Rect] = []

    def set_items(self, items: list[tuple[str, callable]]) -> None:
        self.items = items
        self.scroll = 0
        self.selected = 0

    def toggle(self) -> None:
        self.visible = not self.visible

    def _clamp_view(self) -> None:
        if not self.items:
            self.scroll = 0
            self.selected = 0
            return

        self.selected = max(0, min(self.selected, len(self.items) - 1))

        # keep selected within visible window
        if self.selected < self.scroll:
            self.scroll = self.selected
        if self.selected >= self.scroll + self.max_visible:
            self.scroll = self.selected - self.max_visible + 1

        max_scroll = max(0, len(self.items) - self.max_visible)
        self.scroll = max(0, min(self.scroll, max_scroll))

    def _rebuild_layout(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()

        pad = 12
        item_h = 30
        header_h = 30
        width = 330

        visible_count = min(self.max_visible, len(self.items))
        height = header_h + (visible_count * item_h) + pad * 2

        x = w - width - 18
        y = 18

        self.panel = pygame.Rect(x, y, width, height)

        self.item_rects = []
        iy = self.panel.y + pad + header_h
        for i in range(visible_count):
            r = pygame.Rect(self.panel.x + pad, iy + i * item_h, self.panel.w - pad * 2, item_h - 4)
            self.item_rects.append(r)

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.visible or not self.items:
            return

        if event.type == pygame.MOUSEWHEEL:
            # pygame MOUSEWHEEL: y=1 up, y=-1 down
            self.selected -= event.y
            self._clamp_view()
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected -= 1
                self._clamp_view()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected += 1
                self._clamp_view()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                _, cb = self.items[self.selected]
                cb()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    real_index = self.scroll + idx
                    if 0 <= real_index < len(self.items):
                        self.selected = real_index
                        self._clamp_view()
                        _, cb = self.items[self.selected]
                        cb()
                    return

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        self._rebuild_layout(surface)

        # panel
        pygame.draw.rect(surface, (26, 26, 38), self.panel, border_radius=12)
        pygame.draw.rect(surface, (120, 120, 160), self.panel, width=2, border_radius=12)

        # header
        title = self.font_title.render("DEV MENU (F1)", True, (245, 245, 245))
        surface.blit(title, (self.panel.x + 12, self.panel.y + 10))

        if not self.items:
            msg = self.font.render("No dev options.", True, (220, 220, 220))
            surface.blit(msg, (self.panel.x + 12, self.panel.y + 42))
            return

        self._clamp_view()

        # items
        visible_count = min(self.max_visible, len(self.items))
        start = self.scroll
        end = min(len(self.items), start + visible_count)

        for i, real_index in enumerate(range(start, end)):
            label, _ = self.items[real_index]
            rect = self.item_rects[i]

            selected = (real_index == self.selected)
            bg = (55, 65, 95) if selected else (36, 36, 52)
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            pygame.draw.rect(surface, (120, 120, 160), rect, width=1, border_radius=8)

            txt = self.font.render(label, True, (245, 245, 245))
            surface.blit(txt, txt.get_rect(midleft=(rect.x + 10, rect.centery)))

        # scroll indicator
        if len(self.items) > self.max_visible:
            info = f"{self.scroll + 1}-{min(self.scroll + self.max_visible, len(self.items))}/{len(self.items)}"
            hint = self.font.render(info, True, (200, 200, 200))
            surface.blit(hint, hint.get_rect(midright=(self.panel.right - 12, self.panel.y + 16)))