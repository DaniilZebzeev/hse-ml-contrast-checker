"""CSS Color Parser with support for hex, rgb, rgba, hsl, hsla formats."""

import re
from dataclasses import dataclass
from typing import Tuple, Optional, Dict


@dataclass
class RGBA:
    """RGBA color representation."""

    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    a: float  # 0.0-1.0

    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple."""
        return (self.r, self.g, self.b)

    def __str__(self) -> str:
        """String representation."""
        if self.a < 1.0:
            return f"rgba({self.r}, {self.g}, {self.b}, {self.a:.3f})"
        return f"rgb({self.r}, {self.g}, {self.b})"


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """
    Convert HSL to RGB.

    Args:
        h: Hue (0-360)
        s: Saturation (0-100)
        l: Lightness (0-100)

    Returns:
        RGB tuple (0-255, 0-255, 0-255)
    """
    # Normalize
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0

    if s == 0:
        # Achromatic
        rgb_val = int(l * 255)
        return (rgb_val, rgb_val, rgb_val)

    def hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q

    r = hue_to_rgb(p, q, h + 1 / 3)
    g = hue_to_rgb(p, q, h)
    b = hue_to_rgb(p, q, h - 1 / 3)

    return (int(r * 255), int(g * 255), int(b * 255))


def parse_css_color(color: str) -> RGBA:
    """
    Parse CSS color string to RGBA.

    Supports:
    - Hex: #RGB, #RRGGBB, #RRGGBBAA
    - rgb/rgba: rgb(r, g, b), rgba(r, g, b, a)
    - hsl/hsla: hsl(h, s%, l%), hsla(h, s%, l%, a)
    - Named colors (basic set)

    Args:
        color: CSS color string

    Returns:
        RGBA object

    Raises:
        ValueError: If color format is not recognized
    """
    color = color.strip().lower()

    # Named colors (basic set)
    named_colors = {
        "white": "#ffffff",
        "black": "#000000",
        "red": "#ff0000",
        "green": "#008000",
        "blue": "#0000ff",
        "yellow": "#ffff00",
        "cyan": "#00ffff",
        "magenta": "#ff00ff",
        "gray": "#808080",
        "grey": "#808080",
        "transparent": "#00000000",
    }

    if color in named_colors:
        color = named_colors[color]

    # Hex format
    if color.startswith("#"):
        hex_color = color[1:]

        # #RGB -> #RRGGBB
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])

        # #RRGGBB
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return RGBA(r, g, b, 1.0)

        # #RRGGBBAA
        if len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16) / 255.0
            return RGBA(r, g, b, a)

    # rgb/rgba format
    rgb_match = re.match(r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)", color)
    if rgb_match:
        r = int(rgb_match.group(1))
        g = int(rgb_match.group(2))
        b = int(rgb_match.group(3))
        a = float(rgb_match.group(4)) if rgb_match.group(4) else 1.0
        return RGBA(r, g, b, a)

    # hsl/hsla format
    hsl_match = re.match(r"hsla?\s*\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%\s*(?:,\s*([\d.]+))?\s*\)", color)
    if hsl_match:
        h = float(hsl_match.group(1))
        s = float(hsl_match.group(2))
        l = float(hsl_match.group(3))
        a = float(hsl_match.group(4)) if hsl_match.group(4) else 1.0
        r, g, b = hsl_to_rgb(h, s, l)
        return RGBA(r, g, b, a)

    raise ValueError(f"Unrecognized color format: {color}")


def blend_over(over: RGBA, under: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Blend RGBA color over RGB background using alpha compositing.

    Formula: result = over * alpha + under * (1 - alpha)

    Args:
        over: Top color (RGBA)
        under: Bottom color (RGB tuple)

    Returns:
        Blended RGB tuple
    """
    if over.a >= 1.0:
        return over.to_rgb_tuple()

    alpha = over.a
    r = int(over.r * alpha + under[0] * (1 - alpha))
    g = int(over.g * alpha + under[1] * (1 - alpha))
    b = int(over.b * alpha + under[2] * (1 - alpha))

    return (r, g, b)


def parse_style(style_str: str) -> Dict[str, str]:
    """
    Parse CSS style string to dictionary.

    Args:
        style_str: CSS style string (e.g., "color: red; font-size: 16px")

    Returns:
        Dictionary of style properties
    """
    style_dict = {}

    if not style_str:
        return style_dict

    # Split by semicolon
    declarations = style_str.split(";")

    for decl in declarations:
        decl = decl.strip()
        if ":" not in decl:
            continue

        prop, value = decl.split(":", 1)
        prop = prop.strip().lower()
        value = value.strip()

        style_dict[prop] = value

    return style_dict


def parse_font_size_px(font_size: str) -> Optional[float]:
    """
    Parse font-size string to pixels.

    Supports: px, pt, em (assumes 16px base), rem (assumes 16px base)

    Args:
        font_size: Font size string (e.g., "16px", "12pt", "1.5em")

    Returns:
        Font size in pixels, or None if parsing fails
    """
    font_size = font_size.strip().lower()

    # px
    if font_size.endswith("px"):
        try:
            return float(font_size[:-2])
        except ValueError:
            return None

    # pt (1pt = 1.333px)
    if font_size.endswith("pt"):
        try:
            return float(font_size[:-2]) * 1.333
        except ValueError:
            return None

    # em/rem (assume 16px base)
    if font_size.endswith("em") or font_size.endswith("rem"):
        try:
            return float(font_size[: -len("em")]) * 16.0
        except ValueError:
            return None

    # Try as raw number (assume px)
    try:
        return float(font_size)
    except ValueError:
        return None


def extract_color_from_style(style_str: str, default_color: str = "#000000") -> RGBA:
    """
    Extract color from CSS style string.

    Args:
        style_str: CSS style string
        default_color: Default color if not found

    Returns:
        RGBA object
    """
    style_dict = parse_style(style_str)
    color_str = style_dict.get("color", default_color)
    return parse_css_color(color_str)
