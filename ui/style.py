from __future__ import annotations
import os
import sys
import pygame


def resource_path(relative_path: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative_path)


_FONT_PATH = resource_path(os.path.join("assets", "fonts", "pixel.ttf"))
_FONT_CACHE: dict[int, pygame.font.Font] = {}


def get_font(size: int) -> pygame.font.Font:
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    try:
        font = pygame.font.Font(_FONT_PATH, size)
    except Exception:
        font = pygame.font.Font(None, size)
    _FONT_CACHE[size] = font
    return font


class Fonts:
    @staticmethod
    def title() -> pygame.font.Font:
        return get_font(40)

    @staticmethod
    def ui() -> pygame.font.Font:
        return get_font(22)

    @staticmethod
    def small() -> pygame.font.Font:
        return get_font(18)

    @staticmethod
    def pixel(size: int) -> pygame.font.Font:
        return get_font(size)