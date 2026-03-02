from __future__ import annotations
import pygame

from ui import Button, ButtonStyle
from ui.style import Fonts
from systems.player_render import render_portrait_sprite
from .base import Screen


GENDERS = ["Male", "Female"]

SKIN_TONES = [
    ("Light", (232, 200, 170)),
    ("Tan", (210, 170, 130)),
    ("Brown", (170, 120, 85)),
    ("Dark", (115, 75, 50)),
]

HAIR_COLORS = [
    ("Black", (30, 30, 30)),
    ("Brown", (110, 70, 40)),
    ("Blonde", (210, 190, 90)),
    ("White", (220, 220, 220)),
    ("Red", (170, 70, 60)),
]

EYE_COLORS = [
    ("Blue", (50, 120, 210)),
    ("Green", (55, 170, 110)),
    ("Purple", (145, 85, 195)),
    ("Brown", (90, 65, 45)),
    ("Gray", (160, 160, 160)),
]

HAIR_STYLES_BY_GENDER = {
    "Male": ["Buzz", "Short", "Spiky", "Side Part", "Messy", "Curly"],
    "Female": ["Bob", "Ponytail", "Long", "Wavy", "Bangs", "Twin Tails"],
}


class CharacterCreateScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.font_title = Fonts.title()
        self.font = Fonts.ui()
        self.font_small = Fonts.small()

        self.style = ButtonStyle()

        self.gender_i = 0
        self.skin_i = 0
        self.hair_style_i = 0
        self.hair_color_i = 0
        self.eye_color_i = 0

        self.container = pygame.Rect(0, 0, 1, 1)
        self.left_panel = pygame.Rect(0, 0, 1, 1)
        self.right_panel = pygame.Rect(0, 0, 1, 1)

        self._rows: list[dict] = []
        self.back_btn: Button | None = None
        self.continue_btn: Button | None = None

    def _current_gender(self) -> str:
        return GENDERS[self.gender_i]

    def _hair_styles(self) -> list[str]:
        return HAIR_STYLES_BY_GENDER[self._current_gender()]

    def _cycle(self, attr: str, delta: int, length: int) -> None:
        v = getattr(self, attr)
        setattr(self, attr, (v + delta) % length)

    def on_enter(self) -> None:
        self._rebuild_layout()

    def _rebuild_layout(self) -> None:
        surface = pygame.display.get_surface()
        w, h = surface.get_size() if surface else (1400, 800)

        container_w = min(1000, w - 80)
        container_h = min(600, h - 80)
        self.container = pygame.Rect((w - container_w) // 2, (h - container_h) // 2, container_w, container_h)

        inner_pad = 18
        gap = 18

        panels_h = self.container.h - inner_pad * 2 - 76
        panels_y = self.container.y + inner_pad

        left_w = int(self.container.w * 0.52)
        self.left_panel = pygame.Rect(self.container.x + inner_pad, panels_y, left_w, panels_h)
        self.right_panel = pygame.Rect(
            self.left_panel.right + gap,
            panels_y,
            self.container.right - (self.left_panel.right + gap) - inner_pad,
            panels_h,
        )

        row_count = 5
        top_padding = 56
        bottom_padding = 18
        usable_h = max(240, self.left_panel.h - top_padding - bottom_padding)

        row_h = 44
        row_gap = max(14, (usable_h - row_count * row_h) // max(1, row_count - 1))

        arrow_w = 44
        value_w = self.left_panel.w - (arrow_w * 2) - 14 - 14 - 20

        self._rows.clear()
        row_y = self.left_panel.y + top_padding

        def add_row_static(label: str, attr: str, options_len: int, on_change=None) -> None:
            nonlocal row_y
            label_y = row_y - 22
            left_rect = pygame.Rect(self.left_panel.x + 14, row_y, arrow_w, row_h)
            value_rect = pygame.Rect(left_rect.right + 10, row_y, value_w, row_h)
            right_rect = pygame.Rect(value_rect.right + 10, row_y, arrow_w, row_h)

            def left_click():
                self._cycle(attr, -1, options_len)
                if on_change:
                    on_change()

            def right_click():
                self._cycle(attr, 1, options_len)
                if on_change:
                    on_change()

            self._rows.append({
                "label": label,
                "label_y": label_y,
                "attr": attr,
                "value_rect": value_rect,
                "btn_left": Button(left_rect, "<", left_click, font=self.font, style=self.style),
                "btn_right": Button(right_rect, ">", right_click, font=self.font, style=self.style),
            })
            row_y += row_h + row_gap

        def add_row_dynamic_len(label: str, attr: str, get_len) -> None:
            nonlocal row_y
            label_y = row_y - 22
            left_rect = pygame.Rect(self.left_panel.x + 14, row_y, arrow_w, row_h)
            value_rect = pygame.Rect(left_rect.right + 10, row_y, value_w, row_h)
            right_rect = pygame.Rect(value_rect.right + 10, row_y, arrow_w, row_h)

            def left_click():
                self._cycle(attr, -1, max(1, int(get_len())))

            def right_click():
                self._cycle(attr, 1, max(1, int(get_len())))

            self._rows.append({
                "label": label,
                "label_y": label_y,
                "attr": attr,
                "value_rect": value_rect,
                "btn_left": Button(left_rect, "<", left_click, font=self.font, style=self.style),
                "btn_right": Button(right_rect, ">", right_click, font=self.font, style=self.style),
            })
            row_y += row_h + row_gap

        def gender_changed():
            self.hair_style_i %= len(self._hair_styles())

        add_row_static("Gender", "gender_i", len(GENDERS), on_change=gender_changed)
        add_row_static("Skin Tone", "skin_i", len(SKIN_TONES))
        add_row_dynamic_len("Hair Style", "hair_style_i", get_len=lambda: len(self._hair_styles()))
        add_row_static("Hair Color", "hair_color_i", len(HAIR_COLORS))
        add_row_static("Eye Color", "eye_color_i", len(EYE_COLORS))

        btn_w = 220
        btn_h = 52
        btn_y = self.container.bottom - inner_pad - btn_h

        self.back_btn = Button(
            pygame.Rect(self.container.x + inner_pad, btn_y, btn_w, btn_h),
            "Back",
            self._go_back,
            font=self.font,
            style=self.style,
        )
        self.continue_btn = Button(
            pygame.Rect(self.container.right - inner_pad - btn_w, btn_y, btn_w, btn_h),
            "Continue",
            self._go_next,
            font=self.font,
            style=self.style,
        )

    def _go_back(self) -> None:
        if self.manager:
            from .name_screen import NameScreen
            self.manager.set(NameScreen())

    def _go_next(self) -> None:
        if not self.manager:
            return

        hair_styles = self._hair_styles()
        self.hair_style_i %= len(hair_styles)

        char = self.manager.store.get("character", {})
        char.update({
            "gender": self._current_gender(),
            "skin": SKIN_TONES[self.skin_i][0],
            "skin_rgb": SKIN_TONES[self.skin_i][1],
            "hair_style": hair_styles[self.hair_style_i],
            "hair_color": HAIR_COLORS[self.hair_color_i][0],
            "hair_rgb": HAIR_COLORS[self.hair_color_i][1],
            "eye_color": EYE_COLORS[self.eye_color_i][0],
            "eye_rgb": EYE_COLORS[self.eye_color_i][1],
        })
        self.manager.store["character"] = char

        from .class_select_screen import ClassSelectScreen
        self.manager.set(ClassSelectScreen())

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_back()
            return
        if event.type == pygame.VIDEORESIZE:
            self._rebuild_layout()
            return

        for r in self._rows:
            r["btn_left"].handle_event(event)
            r["btn_right"].handle_event(event)

        if self.back_btn:
            self.back_btn.handle_event(event)
        if self.continue_btn:
            self.continue_btn.handle_event(event)

    def _draw_value_box(self, surface: pygame.Surface, rect: pygame.Rect, text: str, swatch=None) -> None:
        pygame.draw.rect(surface, (40, 40, 60), rect, border_radius=10)
        pygame.draw.rect(surface, (120, 120, 160), rect, width=2, border_radius=10)

        x = rect.x + 12
        if swatch is not None:
            sw = pygame.Rect(x, rect.y + 10, 24, rect.h - 20)
            pygame.draw.rect(surface, swatch, sw, border_radius=6)
            pygame.draw.rect(surface, (10, 10, 14), sw, width=2, border_radius=6)
            x = sw.right + 10

        label = self.font.render(text, True, (240, 240, 240))
        surface.blit(label, label.get_rect(midleft=(x, rect.centery)))

    def _render_preview(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (78, 92, 135), self.right_panel, border_radius=16)
        pygame.draw.rect(surface, (205, 215, 245), self.right_panel, width=2, border_radius=16)

        surface.blit(
            self.font_small.render("Live Preview", True, (245, 245, 250)),
            (self.right_panel.x + 14, self.right_panel.y + 12),
        )

        hair_styles = self._hair_styles()
        self.hair_style_i %= len(hair_styles)

        data = {
            "gender": self._current_gender(),
            "skin_rgb": SKIN_TONES[self.skin_i][1],
            "hair_rgb": HAIR_COLORS[self.hair_color_i][1],
            "eye_rgb": EYE_COLORS[self.eye_color_i][1],
            "hair_style": hair_styles[self.hair_style_i],
        }

        tiny = render_portrait_sprite(data, class_id="Warrior", equipment=None, size=(64, 96))

        max_w = self.right_panel.w - 44
        max_h = self.right_panel.h - 92
        scale = max(2, min(max_w // 64, max_h // 96))
        scaled = pygame.transform.scale(tiny, (64 * scale, 96 * scale))
        rect = scaled.get_rect(center=(self.right_panel.centerx, self.right_panel.centery + 14))

        frame = rect.inflate(20, 20)
        pygame.draw.rect(surface, (30, 36, 56), frame, border_radius=14)
        pygame.draw.rect(surface, (225, 235, 255), frame, width=2, border_radius=14)

        surface.blit(scaled, rect)

    def render(self, surface: pygame.Surface) -> None:
        w, _ = surface.get_size()

        title = self.font_title.render("Character Designer", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(w // 2, self.container.y - 26)))

        pygame.draw.rect(surface, (22, 22, 32), self.container, border_radius=18)
        pygame.draw.rect(surface, (105, 105, 140), self.container, width=2, border_radius=18)

        pygame.draw.rect(surface, (28, 28, 40), self.left_panel, border_radius=16)
        pygame.draw.rect(surface, (105, 105, 140), self.left_panel, width=2, border_radius=16)
        surface.blit(self.font_small.render("Customize", True, (200, 200, 200)),
                     (self.left_panel.x + 14, self.left_panel.y + 12))

        hair_styles = self._hair_styles()
        self.hair_style_i %= len(hair_styles)

        for r in self._rows:
            label = self.font_small.render(r["label"], True, (200, 200, 200))
            surface.blit(label, (self.left_panel.x + 14, r["label_y"]))

            attr = r["attr"]
            if attr == "gender_i":
                text, swatch = self._current_gender(), None
            elif attr == "skin_i":
                text, swatch = SKIN_TONES[self.skin_i][0], SKIN_TONES[self.skin_i][1]
            elif attr == "hair_style_i":
                text, swatch = hair_styles[self.hair_style_i], None
            elif attr == "hair_color_i":
                text, swatch = HAIR_COLORS[self.hair_color_i][0], HAIR_COLORS[self.hair_color_i][1]
            else:
                text, swatch = EYE_COLORS[self.eye_color_i][0], EYE_COLORS[self.eye_color_i][1]

            self._draw_value_box(surface, r["value_rect"], text, swatch)
            r["btn_left"].render(surface)
            r["btn_right"].render(surface)

        self._render_preview(surface)

        if self.back_btn:
            self.back_btn.render(surface)
        if self.continue_btn:
            self.continue_btn.render(surface)