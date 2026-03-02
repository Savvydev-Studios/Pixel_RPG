from __future__ import annotations
import pygame


class Controls:
    """
    Action-based input mapping.
    Each action can have multiple keys (primary + secondary).
    Later, rebinding = editing this map (or loading it from save/settings).
    """

    binds: dict[str, tuple[int, ...]] = {
        # Movement
        "move_up": (pygame.K_w, pygame.K_UP),
        "move_down": (pygame.K_s, pygame.K_DOWN),
        "move_left": (pygame.K_a, pygame.K_LEFT),
        "move_right": (pygame.K_d, pygame.K_RIGHT),

        # Actions
        "confirm": (pygame.K_RETURN, pygame.K_SPACE),
        "cancel": (pygame.K_ESCAPE, pygame.K_BACKSPACE),
        "sprint": (pygame.K_LSHIFT, pygame.K_RSHIFT),
        "interact": (pygame.K_e,),

        # Dev
        "dev_menu": (pygame.K_F1,),
    }

    @staticmethod
    def pressed(keys, action: str) -> bool:
        """Held this frame (use with pygame.key.get_pressed())."""
        return any(keys[k] for k in Controls.binds.get(action, ()))

    @staticmethod
    def keydown(event: pygame.event.Event, action: str) -> bool:
        """Pressed this event (use inside handle_event())."""
        return event.type == pygame.KEYDOWN and event.key in Controls.binds.get(action, ())