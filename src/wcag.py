"""WCAG 2.2 Contrast Ratio Calculator and Classifier.

Implements contrast ratio calculation and classification according to
Web Content Accessibility Guidelines (WCAG) 2.2.
"""

from typing import Tuple, Dict, List, Any
import math
from .wcag_constants import (
    SRGB_GAMMA,
    SRGB_A,
    SRGB_DIV_LOW,
    SRGB_DIV_HIGH,
    LUMA_R,
    LUMA_G,
    LUMA_B,
    CONTRAST_K,
    AA_NORMAL,
    AAA_NORMAL,
    AA_LARGE,
    AAA_LARGE,
    DARKEN_FACTORS,
    LIGHTEN_FACTORS,
)


def compute_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance of an RGB color.

    Formula from WCAG 2.2:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B

    Where R, G, B are calculated as:
    - If RsRGB <= 0.03928: R = RsRGB / 12.92
    - Else: R = ((RsRGB + 0.055) / 1.055) ^ 2.4

    Args:
        rgb: RGB tuple (0-255, 0-255, 0-255)

    Returns:
        Relative luminance (0.0-1.0)

    Example:
        >>> compute_relative_luminance((255, 255, 255))  # White
        1.0
        >>> compute_relative_luminance((0, 0, 0))  # Black
        0.0
    """
    r, g, b = rgb

    # Convert to 0.0-1.0 range
    r_srgb = r / 255.0
    g_srgb = g / 255.0
    b_srgb = b / 255.0

    # Apply gamma correction
    def _linearize(c: float) -> float:
        if c <= 0.03928:
            return c / SRGB_DIV_LOW
        return math.pow((c + SRGB_A) / SRGB_DIV_HIGH, SRGB_GAMMA)

    r_linear = _linearize(r_srgb)
    g_linear = _linearize(g_srgb)
    b_linear = _linearize(b_srgb)

    # Calculate luminance
    luminance = LUMA_R * r_linear + LUMA_G * g_linear + LUMA_B * b_linear

    return luminance


def compute_contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """
    Calculate contrast ratio between two colors.

    Formula from WCAG 2.2:
    (L1 + 0.05) / (L2 + 0.05)
    Where L1 is the lighter color's luminance, L2 is the darker color's luminance.

    Args:
        color1: RGB tuple
        color2: RGB tuple

    Returns:
        Contrast ratio (1.0-21.0)

    Example:
        >>> compute_contrast_ratio((0, 0, 0), (255, 255, 255))  # Black vs White
        21.0
    """
    lum1 = compute_relative_luminance(color1)
    lum2 = compute_relative_luminance(color2)

    # Ensure L1 is lighter
    if lum1 < lum2:
        lum1, lum2 = lum2, lum1

    ratio = (lum1 + CONTRAST_K) / (lum2 + CONTRAST_K)

    return ratio


def classify_contrast_level(ratio: float, font_size_px: float, font_weight: str) -> Dict[str, bool]:
    """
    Classify contrast ratio according to WCAG 2.2 standards.

    WCAG 2.2 Levels:
    - AA Normal text: 4.5:1
    - AA Large text: 3:1
    - AAA Normal text: 7:1
    - AAA Large text: 4.5:1

    Large text definition:
    - 18pt (24px) and larger, OR
    - 14pt (18.67px) and larger if bold (weight >= 700)

    Args:
        ratio: Contrast ratio
        font_size_px: Font size in pixels
        font_weight: Font weight ('normal', 'bold', or numeric string)

    Returns:
        Dictionary with AA_normal, AA_large, AAA keys (bool values)

    Example:
        >>> classify_contrast_level(4.6, 16, 'normal')
        {'AA_normal': True, 'AA_large': True, 'AAA': False}
    """
    # Determine if large text
    is_large = False
    if font_size_px >= 24:
        is_large = True
    elif font_size_px >= 18.67:
        # Check if bold
        if font_weight in ("bold", "bolder"):
            is_large = True
        elif font_weight.isdigit() and int(font_weight) >= 700:
            is_large = True

    # WCAG thresholds
    if is_large:
        aa_threshold = AA_LARGE
        aaa_threshold = AAA_LARGE
    else:
        aa_threshold = AA_NORMAL
        aaa_threshold = AAA_NORMAL

    return {
        "AA_normal": ratio >= AA_NORMAL,
        "AA_large": ratio >= AA_LARGE,
        "AAA": ratio >= aaa_threshold,
        "is_large_text": is_large,
    }


def suggest_contrast_fixes(
    current_ratio: float,
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    font_size_px: float,
    font_weight: str,
) -> List[Dict[str, Any]]:
    """
    Generate recommendations for improving contrast.

    Strategies:
    1. Invert text color
    2. Change text to black or white
    3. Darken or lighten background
    4. Increase font size (to qualify as "large text")
    5. Add text shadow/outline

    Args:
        current_ratio: Current contrast ratio
        text_rgb: Text color RGB tuple
        bg_rgb: Background color RGB tuple
        font_size_px: Font size in pixels
        font_weight: Font weight

    Returns:
        List of suggestion dictionaries with:
        - type: Suggestion type
        - description: Human-readable description
        - new_value: Suggested CSS value
        - expected_ratio: Expected new contrast ratio (if calculable)

    Example:
        >>> fixes = suggest_contrast_fixes(2.5, (100, 100, 100), (200, 200, 200), 16, 'normal')
        >>> fixes[0]['type']
        'change_text_color'
    """
    suggestions: List[Dict[str, Any]] = []

    # Determine target ratio based on current font
    wcag_class = classify_contrast_level(current_ratio, font_size_px, font_weight)
    is_large = wcag_class["is_large_text"]
    target_ratio = AA_LARGE if is_large else AA_NORMAL

    if current_ratio >= target_ratio:
        return suggestions  # Already passes

    # 1. Invert text color
    inverted_text = (255 - text_rgb[0], 255 - text_rgb[1], 255 - text_rgb[2])
    inv_ratio = compute_contrast_ratio(inverted_text, bg_rgb)
    if inv_ratio >= target_ratio:
        suggestions.append(
            {
                "type": "invert_text_color",
                "description": "Инвертировать цвет текста",
                "new_value": f"#{inverted_text[0]:02x}{inverted_text[1]:02x}{inverted_text[2]:02x}",
                "expected_ratio": round(inv_ratio, 2),
            }
        )

    # 2. Change text to black or white
    for new_text, name in [((0, 0, 0), "black"), ((255, 255, 255), "white")]:
        new_ratio = compute_contrast_ratio(new_text, bg_rgb)
        if new_ratio >= target_ratio:
            suggestions.append(
                {
                    "type": "change_text_color",
                    "description": f"Изменить цвет текста на {name}",
                    "new_value": f"#{new_text[0]:02x}{new_text[1]:02x}{new_text[2]:02x}",
                    "expected_ratio": round(new_ratio, 2),
                }
            )

    # 3. Darken background
    for factor in DARKEN_FACTORS:
        darkened_bg = (int(bg_rgb[0] * factor), int(bg_rgb[1] * factor), int(bg_rgb[2] * factor))
        dark_ratio = compute_contrast_ratio(text_rgb, darkened_bg)
        if dark_ratio >= target_ratio:
            suggestions.append(
                {
                    "type": "darken_background",
                    "description": f"Затемнить фон на {int((1-factor)*100)}%",
                    "new_value": f"rgb({darkened_bg[0]}, {darkened_bg[1]}, {darkened_bg[2]})",
                    "expected_ratio": round(dark_ratio, 2),
                }
            )
            break

    # 4. Lighten background
    for factor in LIGHTEN_FACTORS:
        lightened_bg = (
            min(255, int(bg_rgb[0] * factor)),
            min(255, int(bg_rgb[1] * factor)),
            min(255, int(bg_rgb[2] * factor)),
        )
        light_ratio = compute_contrast_ratio(text_rgb, lightened_bg)
        if light_ratio >= target_ratio:
            suggestions.append(
                {
                    "type": "lighten_background",
                    "description": f"Осветлить фон на {int((factor-1)*100)}%",
                    "new_value": f"rgb({lightened_bg[0]}, {lightened_bg[1]}, {lightened_bg[2]})",
                    "expected_ratio": round(light_ratio, 2),
                }
            )
            break

    # 5. Increase font size (to qualify as "large text" with lower threshold)
    if font_size_px < 24:
        # Calculate if current ratio would pass as large text
        large_text_threshold = AA_LARGE
        if current_ratio >= large_text_threshold:
            suggestions.append(
                {
                    "type": "increase_font_size",
                    "description": f"Увеличить размер шрифта до ≥24px (порог AA large: 3:1, текущий: {round(current_ratio, 2)}:1)",
                    "new_value": "24px",
                    "expected_ratio": round(current_ratio, 2),
                }
            )

    # 6. Add text shadow/outline (visual enhancement, doesn't affect measured contrast)
    if len(suggestions) < 3:  # Only suggest if few other options
        suggestions.append(
            {
                "type": "add_text_shadow",
                "description": "Добавить тень текста для улучшения читаемости (не влияет на измеряемый контраст)",
                "new_value": "text-shadow: 0 0 4px rgba(0,0,0,0.8)",
                "expected_ratio": None,
            }
        )

    return suggestions
