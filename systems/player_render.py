from __future__ import annotations
from dataclasses import dataclass
import pygame


# Logical grid for portrait/battle sprite. Scaled up with nearest neighbor.
LW, LH = 32, 48


def _clamp(x: int) -> int:
    return 0 if x < 0 else 255 if x > 255 else x


def _shade(rgb: tuple[int, int, int], d: int) -> tuple[int, int, int]:
    r, g, b = rgb
    return (_clamp(r + d), _clamp(g + d), _clamp(b + d))


def _rect(x0: int, y0: int, w: int, h: int) -> set[tuple[int, int]]:
    return {(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)}


def _circle(cx: int, cy: int, r: int) -> set[tuple[int, int]]:
    pts: set[tuple[int, int]] = set()
    for y in range(LH):
        for x in range(LW):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                pts.add((x, y))
    return pts


def _outline(pixels: set[tuple[int, int]]) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for x, y in pixels:
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < LW and 0 <= ny < LH and (nx, ny) not in pixels:
                out.add((nx, ny))
    return out


def _draw(surf: pygame.Surface, scale: int, pixels: set[tuple[int, int]], color) -> None:
    if not pixels:
        return
    for x, y in pixels:
        surf.fill(color, pygame.Rect(x * scale, y * scale, scale, scale))


# -------------------------
# Data shapes (placeholders for now)
# -------------------------

CLASS_IDS = [
    "Warrior", "Tank", "Rogue", "Mage",
    "Ranger", "Cleric", "Berserker", "Assassin",
]

# We are NOT implementing stats yet. This is just the data hook.
CLASS_DEFAULTS = {
    "Warrior": {"hp": 12, "atk": 8, "def": 7, "int": 3},
    "Tank": {"hp": 16, "atk": 6, "def": 10, "int": 2},
    "Rogue": {"hp": 10, "atk": 9, "def": 5, "int": 3},
    "Mage": {"hp": 8, "atk": 3, "def": 4, "int": 10},
    "Ranger": {"hp": 10, "atk": 8, "def": 5, "int": 4},
    "Cleric": {"hp": 11, "atk": 5, "def": 6, "int": 7},
    "Berserker": {"hp": 12, "atk": 10, "def": 4, "int": 2},
    "Assassin": {"hp": 9, "atk": 10, "def": 4, "int": 3},
}


@dataclass(frozen=True)
class Layer:
    pixels: set[tuple[int, int]]
    color: tuple[int, int, int]


# -------------------------
# Portrait anatomy anchors
# -------------------------
HCX, HCY, HR = 16, 12, 6
EYE_Y = 12


# -------------------------
# Hair masks (editable templates)
# IMPORTANT: these are *only* for portrait/battle (not overworld)
# -------------------------

def hair_mask(gender: str, style: str) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """Return (back, front) hair pixel masks."""
    g = gender
    s = style

    # Male
    if g == "Male":
        if s == "Buzz":
            return set(), _rect(11, 6, 10, 3)
        if s == "Short":
            return set(), _rect(10, 5, 12, 4) | {(10, 9), (21, 9)}
        if s == "Spiky":
            return set(), _rect(10, 6, 12, 3) | {(12, 4), (14, 4), (16, 3), (18, 4), (20, 4)}
        if s == "Side Part":
            return set(), _rect(10, 5, 12, 4) | _rect(10, 9, 6, 2)
        # fallback:
        return set(), _rect(10, 5, 12, 4)

    # Female (make silhouettes *obviously* feminine: longer sides, bangs, ponytails)
    if g == "Female":
        if s == "Bob":
            back = _rect(9, 10, 14, 8) | {(9, 18), (22, 18)}
            front = _rect(10, 5, 12, 4)
            return back, front

        if s == "Bangs":
            back = _rect(9, 10, 14, 7) | {(9, 17), (22, 17)}
            # bangs are a curved-ish band under the top hair
            front = _rect(10, 5, 12, 4) | {(11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (16, 9), (17, 9), (18, 9), (19, 9), (20, 9)}
            return back, front

        if s == "Long":
            # longer side locks + back sheet
            back = _rect(8, 10, 16, 18) | {(8, 28), (23, 28)}
            # two front locks
            back |= _rect(7, 14, 3, 10) | _rect(22, 14, 3, 10)
            front = _rect(10, 5, 12, 4)
            return back, front

        if s == "Wavy":
            # wave bumps on sides + long back
            back = _rect(8, 10, 16, 18)
            back |= {(7, 16), (7, 18), (7, 20), (24, 16), (24, 18), (24, 20)}
            back |= _rect(7, 14, 3, 12) | _rect(22, 14, 3, 12)
            front = _rect(10, 5, 12, 4)
            return back, front

        if s == "Ponytail":
            back = _rect(9, 10, 14, 8) | _rect(22, 16, 4, 14) | {(21, 19), (26, 22), (21, 25), (26, 27)}
            front = _rect(10, 5, 12, 4)
            return back, front

        if s == "Twin Tails":
            # clear twin tails (not a guy cut): long pigtails + head hair
            back = _rect(9, 10, 14, 7)
            back |= _rect(5, 16, 4, 16) | _rect(23, 16, 4, 16)
            back |= {(4, 18), (4, 22), (4, 26), (28, 18), (28, 22), (28, 26)}
            front = _rect(10, 5, 12, 4)
            return back, front

        # fallback:
        return _rect(9, 10, 14, 8), _rect(10, 5, 12, 4)

    # Unknown gender fallback
    return set(), _rect(10, 5, 12, 4)


# -------------------------
# Base outfits (FOUNDATION ONLY)
# Key: (gender, class_id)
# These are intentionally simple silhouettes but class-distinct.
# We'll add detail later by editing these masks.
# -------------------------

def base_outfit_layers(gender: str, class_id: str, palette_seed: int = 0) -> list[Layer]:
    # Neutral fantasy palette set
    outline = (8, 8, 12)
    leather = (120, 95, 70)
    cloth = (75, 85, 120)
    metal = (140, 140, 155)
    green = (70, 110, 80)
    red = (130, 70, 65)
    dark = (55, 55, 75)

    # Anatomy sizing differences (beyond hair)
    if gender == "Male":
        shoulder_w, waist_w = 14, 10
    else:
        shoulder_w, waist_w = 13, 9

    torso_top = 20
    torso_h = 16
    torso_left = HCX - shoulder_w // 2
    hips_top = torso_top + torso_h - 2
    hips_left = HCX - waist_w // 2 + 1
    leg_y = hips_top + 4
    leg_h = 14

    # Common pieces
    torso = _rect(torso_left, torso_top, shoulder_w, torso_h)
    hips = _rect(hips_left, hips_top, waist_w, 4)
    left_leg = _rect(HCX - 5, leg_y, 4, leg_h)
    right_leg = _rect(HCX + 1, leg_y + 1, 4, leg_h)
    boots = _rect(HCX - 6, leg_y + leg_h, 6, 3) | _rect(HCX + 0, leg_y + leg_h + 1, 6, 3)

    # Arms (same base; gear can override gloves/bracers later)
    l_arm = _rect(torso_left - 2, torso_top + 4, 3, 10)
    r_arm = _rect(torso_left + shoulder_w - 1, torso_top + 5, 4, 4) | _rect(torso_left + shoulder_w + 1, torso_top + 8, 4, 4)
    l_hand = _rect(torso_left - 2, torso_top + 14, 3, 3)
    r_hand = _rect(torso_left + shoulder_w + 4, torso_top + 8, 3, 3)

    layers: list[Layer] = []

    # Class silhouettes
    if class_id in ("Warrior", "Tank"):
        # armor chest + belt + heavier boots
        chest = torso | _rect(torso_left - 1, torso_top + 2, shoulder_w + 2, 6)  # shoulder plates
        layers.append(Layer(chest, metal))
        layers.append(Layer(_rect(torso_left, torso_top + torso_h - 2, shoulder_w, 2), _shade(metal, -25)))
        layers.append(Layer(hips, _shade(metal, -15)))

        # belt + buckle
        belt = _rect(torso_left + 1, torso_top + torso_h - 4, shoulder_w - 2, 2)
        layers.append(Layer(belt, dark))
        layers.append(Layer(_rect(HCX - 1, torso_top + torso_h - 4, 2, 2), (210, 200, 140)))

        # arms as bracers
        layers.append(Layer(l_arm | r_arm, _shade(metal, -20)))
        layers.append(Layer(l_hand | r_hand, (80, 60, 40)))

        # pants + boots
        layers.append(Layer(left_leg | right_leg, cloth))
        layers.append(Layer(_rect(HCX - 5, leg_y + leg_h - 2, 4, 2) | _rect(HCX + 1, leg_y + leg_h - 1, 4, 2), _shade(cloth, -25)))
        layers.append(Layer(boots, (60, 45, 35)))

        if class_id == "Tank":
            # extra bulk: chest add-on + thicker boots
            layers.append(Layer(_rect(torso_left - 2, torso_top + 6, shoulder_w + 4, 4), _shade(metal, 10)))
            layers.append(Layer(_rect(HCX - 7, leg_y + leg_h, 7, 3) | _rect(HCX - 1, leg_y + leg_h + 1, 7, 3), (55, 40, 30)))

    elif class_id in ("Rogue", "Assassin"):
        # hood/cloak silhouette + dark leather
        cloak = _rect(9, 22, 14, 18) | {(8, 24), (23, 24), (8, 28), (23, 28)}
        layers.append(Layer(cloak, dark))
        layers.append(Layer(_rect(10, 38, 12, 2), _shade(dark, -25)))

        layers.append(Layer(torso, _shade(leather, -10)))
        layers.append(Layer(_rect(torso_left, torso_top, shoulder_w, 3), _shade(leather, 15)))
        layers.append(Layer(hips, _shade(leather, -20)))

        # arms + gloves
        layers.append(Layer(l_arm | r_arm, _shade(leather, -25)))
        layers.append(Layer(l_hand | r_hand, (35, 35, 45)))

        # slim pants + boots
        layers.append(Layer(left_leg | right_leg, _shade(cloth, -15)))
        layers.append(Layer(boots, (45, 38, 32)))

    elif class_id in ("Mage", "Cleric"):
        # robe silhouette
        robe = torso | _rect(torso_left - 1, torso_top + 10, shoulder_w + 2, 8)
        layers.append(Layer(robe, (95, 85, 130) if class_id == "Mage" else (120, 110, 70)))
        layers.append(Layer(_rect(torso_left, torso_top + torso_h - 2, shoulder_w, 2),
                            (75, 65, 110) if class_id == "Mage" else (95, 85, 55)))

        # sleeves
        layers.append(Layer(l_arm | r_arm, (80, 70, 120) if class_id == "Mage" else (105, 95, 65)))
        layers.append(Layer(l_hand | r_hand, (60, 50, 90) if class_id == "Mage" else (85, 75, 50)))

        # robe "legs" (no obvious pants)
        skirt = _rect(HCX - 6, leg_y, 12, 14)
        layers.append(Layer(skirt, (85, 75, 125) if class_id == "Mage" else (110, 100, 65)))
        layers.append(Layer(_rect(HCX - 6, leg_y + 12, 12, 2), (70, 60, 105) if class_id == "Mage" else (90, 80, 55)))
        layers.append(Layer(boots, (50, 40, 35)))

    elif class_id in ("Ranger",):
        # light armor + green accents
        layers.append(Layer(torso, _shade(leather, -5)))
        layers.append(Layer(_rect(torso_left, torso_top + 3, shoulder_w, 3), green))
        layers.append(Layer(hips, _shade(leather, -20)))
        layers.append(Layer(l_arm | r_arm, _shade(leather, -25)))
        layers.append(Layer(l_hand | r_hand, (70, 55, 40)))
        layers.append(Layer(left_leg | right_leg, _shade(cloth, -10)))
        layers.append(Layer(boots, (55, 42, 32)))

        # strap (archer vibe)
        strap = {(HCX - 6, torso_top + 2), (HCX - 5, torso_top + 3), (HCX - 4, torso_top + 4),
                 (HCX - 3, torso_top + 5), (HCX - 2, torso_top + 6), (HCX - 1, torso_top + 7),
                 (HCX, torso_top + 8), (HCX + 1, torso_top + 9), (HCX + 2, torso_top + 10)}
        layers.append(Layer(strap, green))

    elif class_id in ("Berserker",):
        # bare arms + fur-ish belt
        layers.append(Layer(torso, red))
        layers.append(Layer(_rect(torso_left, torso_top + torso_h - 2, shoulder_w, 2), _shade(red, -25)))
        # arms bare
        layers.append(Layer(l_arm | r_arm, _shade((skin[0], skin[1], skin[2]), -10)))
        layers.append(Layer(l_hand | r_hand, _shade((skin[0], skin[1], skin[2]), -25)))
        # fur belt
        layers.append(Layer(_rect(torso_left + 1, torso_top + torso_h - 4, shoulder_w - 2, 2), (95, 80, 55)))
        layers.append(Layer(hips, _shade(red, -20)))
        layers.append(Layer(left_leg | right_leg, _shade(cloth, -20)))
        layers.append(Layer(boots, (50, 38, 30)))

    else:
        # fallback “adventurer”
        layers.append(Layer(torso, leather))
        layers.append(Layer(_rect(torso_left, torso_top, shoulder_w, 3), _shade(leather, 20)))
        layers.append(Layer(hips, _shade(leather, -15)))
        layers.append(Layer(l_arm | r_arm, _shade(leather, -25)))
        layers.append(Layer(l_hand | r_hand, (70, 55, 40)))
        layers.append(Layer(left_leg | right_leg, cloth))
        layers.append(Layer(boots, (60, 45, 35)))

    # NOTE: We do NOT draw outline here. Outline is done once at the end globally.
    return layers


# -------------------------
# Gear overlays (FOUNDATION ONLY)
# slot: "head", "chest", "hands", "feet", "weapon", etc
# key: (slot, item_id, gender, class_id)
# For now, empty. We'll fill later as gear is implemented.
# -------------------------
GEAR_OVERLAYS: dict[tuple[str, str, str, str], list[Layer]] = {}


def gear_layers(gender: str, class_id: str, equipment: dict | None) -> list[Layer]:
    if not equipment:
        return []
    layers: list[Layer] = []
    for slot, item_id in equipment.items():
        key = (slot, item_id, gender, class_id)
        if key in GEAR_OVERLAYS:
            layers.extend(GEAR_OVERLAYS[key])
    return layers


def render_portrait_sprite(
    character: dict,
    class_id: str = "Warrior",
    equipment: dict | None = None,
    size: tuple[int, int] = (64, 96),
) -> pygame.Surface:
    """
    Portrait/Battle sprite renderer.

    This is the FOUNDATION for:
    - class-based base outfits (gender + class)
    - gender/class-dependent gear overlays
    - future art changes without rewrites

    We intentionally keep visuals modest but structured.
    """
    out_w, out_h = size
    scale = out_w // LW  # expect 2 for 64x96

    surf = pygame.Surface((out_w, out_h), pygame.SRCALPHA)

    gender = character.get("gender", "Male")
    hair_style = character.get("hair_style", "Short")
    skin = character.get("skin_rgb", (200, 170, 140))
    hair = character.get("hair_rgb", (30, 30, 30))
    eyes = character.get("eye_rgb", (60, 120, 200))

    outline_c = (8, 8, 12)
    hair_hi = _shade(hair, 70)
    hair_lo = _shade(hair, -25)

    all_pixels: set[tuple[int, int]] = set()

    # ---- Hair back
    back, front = hair_mask(gender, hair_style)
    if back:
        _draw(surf, scale, back, hair)
        # highlight stripe to make black hair visible
        hx = min(x for x, _ in back) + 1
        hy0 = min(y for _, y in back) + 1
        hy1 = max(y for _, y in back) - 1
        _draw(surf, scale, {(hx, y) for y in range(hy0, hy1 + 1)}, hair_hi)
        all_pixels |= back

    # ---- Head
    head = _circle(HCX, HCY, HR)
    _draw(surf, scale, head, skin)
    all_pixels |= head

    # ---- Hair front
    if front:
        _draw(surf, scale, front, hair)
        top_y = min(y for _, y in front)
        bot_y = max(y for _, y in front)
        _draw(surf, scale, {(x, top_y) for x, y in front if y == top_y}, hair_hi)
        _draw(surf, scale, {(x, bot_y) for x, y in front if y == bot_y}, hair_lo)
        all_pixels |= front

    # ---- Eyes
    eye_px = {(HCX - 2, EYE_Y), (HCX + 1, EYE_Y)}
    _draw(surf, scale, eye_px, eyes)
    _draw(surf, scale, {(HCX - 2, EYE_Y - 1), (HCX + 1, EYE_Y - 1)}, _shade(eyes, -25))
    all_pixels |= eye_px

    # ---- Base outfit layers (gender + class)
    base_layers = base_outfit_layers(gender, class_id)
    for layer in base_layers:
        _draw(surf, scale, layer.pixels, layer.color)
        all_pixels |= layer.pixels

    # ---- Gear layers (slot + item_id + gender + class)
    g_layers = gear_layers(gender, class_id, equipment)
    for layer in g_layers:
        _draw(surf, scale, layer.pixels, layer.color)
        all_pixels |= layer.pixels

    # ---- One outline pass (makes it look like real pixel art)
    out = _outline(all_pixels)
    _draw(surf, scale, out, outline_c)

    return surf