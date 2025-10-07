#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contrast_checker.py
-------------------
Self-contained script to compute text-vs-background contrast for slide content with:
- base_color (may be hex8/rgba/hsla with alpha),
- optional custom_theme color (may also include alpha),
- optional background image (whole slide) or image entities under text,
- HTML content containing "entities" with unique ids and text spans with inline styles.

Output: JSON with per-entity minimal contrast and WCAG flags.

USAGE EXAMPLES
--------------
1) Minimal (slide JSON file only; no background image):
   python contrast_checker.py --slide-json slide.json --out result.json

2) With an explicit background image file (PNG/JPG) that is the slide's background:
   python contrast_checker.py --slide-json slide.json --bg-image bg.png --out result.json

3) If your slide JSON is an array of slides, use --slide-index to pick one:
   python contrast_checker.py --slide-json slides.json --slide-index 0 --out result.json

The script has NO placeholders and avoids external network requests.
It uses only the Python standard library + Pillow (PIL) for image handling (optional).
If Pillow is missing and you don't analyze images, it still works (colors-only pipeline).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# Optional dependency for image processing
try:
    from PIL import Image
except Exception:
    Image = None  # type: ignore


# -----------------------------
# Utility: CSS parsing helpers
# -----------------------------

CSS_COLOR_KEYWORDS = {
    # CSS Level 1/2/3 keywords (subset commonly met; full list can be added if needed)
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 128, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "lightgray": (211, 211, 211),
    "lightgrey": (211, 211, 211),
    "darkgray": (169, 169, 169),
    "darkgrey": (169, 169, 169),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "navy": (0, 0, 128),
    "teal": (0, 128, 128),
    "olive": (128, 128, 0),
    "maroon": (128, 0, 0),
    "silver": (192, 192, 192),
    "transparent": (0, 0, 0),  # special-cased with alpha=0
}


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def parse_style(style: str) -> Dict[str, str]:
    """
    Parse inline CSS style string into a dict of lower-case property->value.
    """
    result: Dict[str, str] = {}
    if not style:
        return result
    for part in style.split(";"):
        if not part.strip():
            continue
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        result[k.strip().lower()] = v.strip()
    return result


def parse_length_px(v: str) -> Optional[float]:
    """
    Parse something like '123px' or '12.5px' into float pixels.
    """
    if not v:
        return None
    m = re.search(r"(-?\d+(\.\d+)?)\s*px", v, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


@dataclass
class RGBA:
    r: int
    g: int
    b: int
    a: float = 1.0  # [0..1]

    def clamp255(self) -> "RGBA":
        return RGBA(int(clamp(self.r, 0, 255)), int(clamp(self.g, 0, 255)), int(clamp(self.b, 0, 255)), clamp(self.a, 0.0, 1.0))

    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        c = self.clamp255()
        return (c.r, c.g, c.b)


def parse_css_color(s: Optional[str]) -> Optional[RGBA]:
    """
    Parse a CSS color string (hex3/4/6/8, rgb/rgba, hsl/hsla, keywords).
    Returns RGBA or None.
    """
    if not s:
        return None
    s = s.strip().lower()
    if not s:
        return None

    # Keyword
    if s in CSS_COLOR_KEYWORDS:
        r, g, b = CSS_COLOR_KEYWORDS[s]
        a = 0.0 if s == "transparent" else 1.0
        return RGBA(r, g, b, a)

    # HEX: #rgb, #rgba, #rrggbb, #rrggbbaa
    if s.startswith("#"):
        hexpart = s[1:]
        if len(hexpart) == 3:  # #rgb
            r = int(hexpart[0] * 2, 16)
            g = int(hexpart[1] * 2, 16)
            b = int(hexpart[2] * 2, 16)
            return RGBA(r, g, b, 1.0)
        elif len(hexpart) == 4:  # #rgba
            r = int(hexpart[0] * 2, 16)
            g = int(hexpart[1] * 2, 16)
            b = int(hexpart[2] * 2, 16)
            a = int(hexpart[3] * 2, 16) / 255.0
            return RGBA(r, g, b, a)
        elif len(hexpart) == 6:  # #rrggbb
            r = int(hexpart[0:2], 16)
            g = int(hexpart[2:4], 16)
            b = int(hexpart[4:6], 16)
            return RGBA(r, g, b, 1.0)
        elif len(hexpart) == 8:  # #rrggbbaa
            r = int(hexpart[0:2], 16)
            g = int(hexpart[2:4], 16)
            b = int(hexpart[4:6], 16)
            a = int(hexpart[6:8], 16) / 255.0
            return RGBA(r, g, b, a)

    # rgb(), rgba()
    m = re.match(r"rgba?\(\s*([^\)]+)\)", s)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) >= 3:
            def parse_channel(x: str) -> int:
                if x.endswith("%"):
                    # percentage
                    return int(round(float(x[:-1]) * 2.55))
                return int(float(x))

            r = clamp(parse_channel(parts[0]), 0, 255)
            g = clamp(parse_channel(parts[1]), 0, 255)
            b = clamp(parse_channel(parts[2]), 0, 255)
            a = 1.0
            if len(parts) == 4:
                aa = parts[3]
                if aa.endswith("%"):
                    a = clamp(float(aa[:-1]) / 100.0, 0.0, 1.0)
                else:
                    a = clamp(float(aa), 0.0, 1.0)
            return RGBA(int(r), int(g), int(b), a)

    # hsl(), hsla()
    m = re.match(r"hsla?\(\s*([^\)]+)\)", s)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) >= 3:
            h = float(parts[0].rstrip("deg"))
            s_perc = float(parts[1].rstrip("%"))
            l_perc = float(parts[2].rstrip("%"))
            a = 1.0
            if len(parts) == 4:
                aa = parts[3]
                if aa.endswith("%"):
                    a = clamp(float(aa[:-1]) / 100.0, 0.0, 1.0)
                else:
                    a = clamp(float(aa), 0.0, 1.0)
            r, g, b = hsl_to_rgb(h, s_perc / 100.0, l_perc / 100.0)
            return RGBA(r, g, b, a)

    return None


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    # Convert HSL to RGB, all in [0,1] ranges except h in degrees
    c = (1 - abs(2 * l - 1)) * s
    h_ = (h % 360) / 60.0
    x = c * (1 - abs((h_ % 2) - 1))
    r1 = g1 = b1 = 0.0
    if 0 <= h_ < 1:
        r1, g1, b1 = c, x, 0
    elif 1 <= h_ < 2:
        r1, g1, b1 = x, c, 0
    elif 2 <= h_ < 3:
        r1, g1, b1 = 0, c, x
    elif 3 <= h_ < 4:
        r1, g1, b1 = 0, x, c
    elif 4 <= h_ < 5:
        r1, g1, b1 = x, 0, c
    elif 5 <= h_ < 6:
        r1, g1, b1 = c, 0, x
    m = l - c / 2
    r = int(round((r1 + m) * 255))
    g = int(round((g1 + m) * 255))
    b = int(round((b1 + m) * 255))
    return (int(clamp(r, 0, 255)), int(clamp(g, 0, 255)), int(clamp(b, 0, 255)))


# ---------------------------------------
# Blending, luminance, contrast (WCAG)
# ---------------------------------------

def blend_over(over: RGBA, under: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Alpha-composite OVER on top of UNDER (under has implicit alpha=1).
    """
    a = clamp(over.a, 0.0, 1.0)
    r = int(round(over.r * a + under[0] * (1 - a)))
    g = int(round(over.g * a + under[1] * (1 - a)))
    b = int(round(over.b * a + under[2] * (1 - a)))
    return (r, g, b)


def blend_chain(tops: List[RGBA], bottom: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Composite multiple OVER layers (in order, first item is the TOPMOST).
    Example: blend_chain([base_color, custom_theme], image_pixel)
    Means: put base_color over custom_theme over image.
    """
    res = bottom
    # We apply from LAST to FIRST (bottom-most first) to follow painter's model
    for over in reversed(tops):
        res = blend_over(over, res)
    return res


def srgb_to_linear(c: float) -> float:
    c = clamp(c / 255.0, 0.0, 1.0)
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    r_lin = srgb_to_linear(rgb[0])
    g_lin = srgb_to_linear(rgb[1])
    b_lin = srgb_to_linear(rgb[2])
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> float:
    L1 = relative_luminance(fg)
    L2 = relative_luminance(bg)
    Lmax = max(L1, L2)
    Lmin = min(L1, L2)
    return (Lmax + 0.05) / (Lmin + 0.05)


# ---------------------------------------
# HTML parsing (lightweight, regex-based)
# ---------------------------------------

ENTITY_ID_RE = re.compile(r'id\s*=\s*"(text-[A-Za-z0-9_\-]+)"')
STYLE_RE = re.compile(r'style\s*=\s*"([^"]*)"')
SPAN_RE = re.compile(r'<span[^>]*?>|</span>', re.IGNORECASE)
COLOR_IN_STYLE_RE = re.compile(r'color\s*:\s*([^;]+)', re.IGNORECASE)
FS_IN_STYLE_RE = re.compile(r'font-size\s*:\s*([^;]+)', re.IGNORECASE)
FW_IN_STYLE_RE = re.compile(r'font-weight\s*:\s*([^;]+)', re.IGNORECASE)
WRAPPER_STYLE_RE = re.compile(r'class\s*=\s*"[^"]*entity__wrapper[^"]*"[^>]*style\s*=\s*"([^"]*)"')

def extract_entities_html(content_html: str) -> List[Dict[str, Any]]:
    """
    Very lightweight HTML scanner to find entity blocks and their inner spans.
    Returns list of dicts:
      { "id": "...", "raw": "<div ...>...</div>", "wrapper_style": "...", "spans": [ {"style": "..."} ... ] }
    We assume entities have ids like text-... and are inside a wrapper div with class entity__wrapper that carries geometry.
    """
    entities: List[Dict[str, Any]] = []

    # Split roughly by 'id="text-...' occurrences to isolate entities
    parts = ENTITY_ID_RE.split(content_html)
    # ENTITY_ID_RE splits into [pre, id1, rest1, id2, rest2, ...]
    if len(parts) <= 1:
        return entities

    pre = parts[0]
    for i in range(1, len(parts), 2):
        ent_id = parts[i]
        rest = parts[i + 1] if i + 1 < len(parts) else ""
        # Try to cut this entity HTML until the next entity id or end
        next_match = ENTITY_ID_RE.search(rest)
        if next_match:
            raw = rest[:next_match.start()]
        else:
            raw = rest

        # Find nearest wrapper style before this entity's markup (heuristic)
        # Search backwards from the start of raw in 'pre + raw' for entity__wrapper style
        search_region = pre[-2000:] + raw[:2000]  # limit context
        w = WRAPPER_STYLE_RE.search(search_region)
        wrapper_style = w.group(1) if w else ""

        # Collect spans inside raw
        spans_styles = []
        for m in re.finditer(r'<span[^>]*style\s*=\s*"([^"]*)"', raw, re.IGNORECASE):
            spans_styles.append(m.group(1))

        entities.append({
            "id": ent_id,
            "raw": raw,
            "wrapper_style": wrapper_style,
            "spans_styles": spans_styles,
        })

        pre = rest  # advance

    return entities


def parse_font_size_px(s: str) -> Optional[float]:
    if not s:
        return None
    # match e.g., 18px, 1.5rem (approximate rem=16px), 120%
    m = re.search(r'(-?\d+(\.\d+)?)\s*px', s, re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r'(-?\d+(\.\d+)?)\s*rem', s, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 16.0
    m = re.search(r'(-?\d+(\.\d+)?)\s*%', s, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 16.0 / 100.0
    return None


def parse_font_weight(s: str) -> Optional[str]:
    if not s:
        return None
    m = re.search(r'font-weight\s*:\s*([^;]+)', s, re.IGNORECASE)
    if not m:
        return None
    v = m.group(1).strip().lower()
    # normalize numeric weights
    if v.isdigit():
        n = int(v)
        return "bold" if n >= 600 else "normal"
    return "bold" if "bold" in v else "normal"


# ---------------------------------------
# Image helpers: dominant colors under a region
# ---------------------------------------

def dominant_colors_pil(img: "Image.Image", bbox: Tuple[int, int, int, int], k: int = 5) -> List[Tuple[Tuple[int, int, int], float]]:
    """
    Get top-K dominant colors for a region bbox=(left, top, right, bottom) using Pillow's adaptive palette.
    Returns list of (rgb, weight) with weights summing to ~1.0.
    """
    region = img.crop(bbox)
    # Reduce size for performance
    max_dim = 256
    w, h = region.size
    scale = min(1.0, max_dim / max(w, h)) if max(w, h) > max_dim else 1.0
    if scale < 1.0:
        region = region.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    # Convert to palette with k colors
    pal_img = region.convert("P", palette=Image.ADAPTIVE, colors=max(1, k))
    pal = pal_img.getpalette()
    color_counts = pal_img.getcolors()
    if not color_counts:
        # fallback to average color
        avg = region.resize((1, 1), Image.BOX).getpixel((0, 0))
        if isinstance(avg, tuple) and len(avg) >= 3:
            return [((avg[0], avg[1], avg[2]), 1.0)]
        elif isinstance(avg, int):
            # Index into palette
            idx = avg * 3
            return [((pal[idx], pal[idx+1], pal[idx+2]), 1.0)]
        return [((255, 255, 255), 1.0)]
    total = sum(count for count, _ in color_counts)
    result: List[Tuple[Tuple[int, int, int], float]] = []
    for count, idx in sorted(color_counts, reverse=True):
        r = pal[idx * 3 + 0]
        g = pal[idx * 3 + 1]
        b = pal[idx * 3 + 2]
        result.append(((r, g, b), count / total))
    # Normalize and cap to k entries
    s = sum(w for _, w in result) or 1.0
    result = [ (rgb, w/s) for rgb, w in result[:k] ]
    return result


# ---------------------------------------
# Core analysis per slide
# ---------------------------------------

@dataclass
class EntityResult:
    id: str
    text_colors: List[Dict[str, Any]]
    font: Dict[str, Any]
    bg_under_entity: Dict[str, Any]
    contrast: Dict[str, Any]


def classify_wcag(ratio: float, font_size_px: float, font_weight: str) -> Dict[str, bool]:
    """
    WCAG 2.2 thresholds:
      - AA normal text: 4.5:1
      - AA large text: 3.0:1 (large = >=24px normal or >=18.66px bold ~ 18.66 = 14pt)
      - AAA: 7.0:1 (for normal text)
    """
    is_bold = (font_weight or "normal") == "bold"
    large_threshold = 18.66 if is_bold else 24.0
    is_large = font_size_px >= large_threshold
    return {
        "AA_normal": ratio >= 4.5,
        "AA_large": ratio >= 3.0 and is_large,
        "AAA": ratio >= 7.0,
    }


def analyze_slide(slide: Dict[str, Any], bg_image_path: Optional[str]=None, k_colors: int=5) -> Dict[str, Any]:
    """
    Main per-slide analysis.
    """
    slide_id = slide.get("id") or slide.get("id_slide") or None
    color_text_default = slide.get("color_text") or "#000000"

    # Colors layered from TOP to BOTTOM (painter model): base_color OVER custom_theme OVER image/white
    base_color = parse_css_color(slide.get("base_color")) if slide.get("base_color") else None
    custom_theme = parse_css_color(slide.get("custom_theme")) if slide.get("custom_theme") else None
    overlay_layers: List[RGBA] = []
    if custom_theme:
        overlay_layers.append(custom_theme)
    if base_color:  # base_color has higher priority (should be on top)
        overlay_layers.append(base_color)

    # Prepare background image if available
    pil_img = None
    if Image is not None:
        # prefer explicit argument
        if bg_image_path and os.path.exists(bg_image_path):
            pil_img = Image.open(bg_image_path).convert("RGB")
        else:
            # Try to find any local path in slide_images
            imgs = slide.get("slide_images") or []
            # supported keys: 'path', 'local_path'
            for im in imgs:
                for key in ("path", "local_path", "file"):
                    p = im.get(key) if isinstance(im, dict) else None
                    if p and os.path.exists(p):
                        pil_img = Image.open(p).convert("RGB")
                        break
                if pil_img is not None:
                    break

    # Extract HTML content
    content_html = ""
    # V1: slide has content_slide: [ {"content": "<div ...>...</div>"} ]
    cs = slide.get("content_slide")
    if isinstance(cs, list) and cs and isinstance(cs[0], dict) and "content" in cs[0]:
        content_html = cs[0]["content"]
    # V2: separate request with {"content": "<div ...>...</div>"}
    if not content_html:
        content_html = slide.get("content") or ""

    entities = extract_entities_html(content_html)

    results: List[EntityResult] = []

    # Canvas default underneath everything (common for slide tools)
    canvas_rgb = (255, 255, 255)

    # If there is no image, we can compute one effective background color for entire slide
    global_effective_bg = None
    if pil_img is None:
        global_effective_bg = blend_chain(overlay_layers, canvas_rgb)

    for ent in entities:
        ent_id = ent["id"]
        spans_styles: List[str] = ent.get("spans_styles", [])

        # Collect text colors (unique) + approx coverage (equal weights for spans if unknown length)
        text_colors: List[Tuple[Tuple[int, int, int], str, float]] = []
        if spans_styles:
            portion = 1.0 / len(spans_styles)
            for st in spans_styles:
                # parse color
                m = COLOR_IN_STYLE_RE.search(st or "")
                css_color = m.group(1).strip() if m else color_text_default
                rgba = parse_css_color(css_color) or parse_css_color(color_text_default) or RGBA(0, 0, 0, 1.0)
                text_colors.append((rgba.to_rgb_tuple(), css_color, portion))
        else:
            rgba = parse_css_color(color_text_default) or RGBA(0, 0, 0, 1.0)
            text_colors.append((rgba.to_rgb_tuple(), color_text_default, 1.0))

        # Font size / weight (fallbacks)
        font_size_px = None
        font_weight = None
        for st in spans_styles:
            if font_size_px is None:
                fs = parse_font_size_px(st)
                if fs is not None:
                    font_size_px = fs
            if font_weight is None:
                fw = parse_font_weight(st)
                if fw is not None:
                    font_weight = fw
        if font_size_px is None:
            font_size_px = 16.0
        if font_weight is None:
            font_weight = "normal"

        # Geometry from wrapper style (top/left/width/height)
        left = top = width = height = None
        wrapper_style = ent.get("wrapper_style", "")
        if wrapper_style:
            st = parse_style(wrapper_style)
            left = parse_length_px(st.get("left", ""))
            top = parse_length_px(st.get("top", ""))
            width = parse_length_px(st.get("width", ""))
            height = parse_length_px(st.get("height", ""))

        # Determine background colors under entity
        bg_colors: List[Tuple[Tuple[int, int, int], float]] = []
        if pil_img is not None and all(v is not None for v in (left, top, width, height)):
            # Crop region from image
            L = max(0, int(round(left or 0)))
            T = max(0, int(round(top or 0)))
            R = max(L + 1, int(round((left or 0) + (width or pil_img.width))))
            B = max(T + 1, int(round((top or 0) + (height or pil_img.height))))
            R = min(R, pil_img.width)
            B = min(B, pil_img.height)
            doms = dominant_colors_pil(pil_img, (L, T, R, B), k=k_colors)
            # Apply overlay layers to each dominant color
            effective = []
            for rgb, w in doms:
                eff = blend_chain(overlay_layers, rgb)
                effective.append((eff, w))
            bg_colors = effective
            bg_method = "dominant_color_after_blend"
        elif pil_img is not None:
            # No geometry → use whole image
            doms = dominant_colors_pil(pil_img, (0, 0, pil_img.width, pil_img.height), k=k_colors)
            effective = []
            for rgb, w in doms:
                eff = blend_chain(overlay_layers, rgb)
                effective.append((eff, w))
            bg_colors = effective
            bg_method = "dominant_color_after_blend"
        else:
            # No image → only colors
            eff = global_effective_bg if global_effective_bg else blend_chain(overlay_layers, canvas_rgb)
            bg_colors = [(eff, 1.0)]
            bg_method = "composited_color"

        # Compute minimal contrast for this entity
        per_text = []
        min_ratio = float("inf")
        for rgb_text, css, w_text in text_colors:
            # Worst-case background among dominant bg colors
            worst_for_text = min(contrast_ratio(rgb_text, bg) for bg, w_bg in bg_colors)
            per_text.append({"css": css, "rgb": list(rgb_text), "ratio": round(worst_for_text, 4)})
            min_ratio = min(min_ratio, worst_for_text)

        wcag = classify_wcag(min_ratio, font_size_px, font_weight)

        results.append(EntityResult(
            id=ent_id,
            text_colors=[{"css": t["css"], "rgb": t["rgb"], "coverage": 1.0/len(text_colors) if len(text_colors)>0 else 1.0} for t in per_text],
            font={"size_px": round(float(font_size_px), 2), "weight": font_weight},
            bg_under_entity={
                "method": bg_method,
                "colors": [{"rgb": list(rgb), "weight": round(float(w), 4)} for (rgb, w) in bg_colors]
            },
            contrast={
                "min_ratio": round(min_ratio, 4),
                "by_text_color": per_text,
                "wcag": wcag
            }
        ))

    # Prepare final JSON
    out = {
        "slide_id": slide_id,
        "background": {
            "source": "image+colors" if pil_img is not None else "colors_only",
            "effective_rgb": list(global_effective_bg) if global_effective_bg else None
        },
        "entities": [er.__dict__ for er in results]
    }
    return out


# ---------------------------------------
# CLI
# ---------------------------------------

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Compute text/background contrast for slide HTML+JSON (WCAG 2.2).")
    parser.add_argument("--slide-json", required=True, help="Path to slide JSON (object or array).")
    parser.add_argument("--slide-index", type=int, default=None, help="If the JSON is an array, index of the slide to analyze.")
    parser.add_argument("--bg-image", default=None, help="Optional path to a background image file for the slide (if not provided in JSON).")
    parser.add_argument("--k", type=int, default=5, help="Number of dominant colors to extract from background regions.")
    parser.add_argument("--out", default=None, help="Output path for result JSON (also printed to stdout).")
    args = parser.parse_args()

    data = load_json(args.slide_json)

    # If the file is an array of slides
    if isinstance(data, list):
        idx = args.slide_index if args.slide_index is not None else 0
        if idx < 0 or idx >= len(data):
            print(f"ERROR: --slide-index {idx} is out of range for array with length {len(data)}", file=sys.stderr)
            sys.exit(3)
        slide = data[idx]
    else:
        slide = data

    result = analyze_slide(slide, bg_image_path=args.bg_image, k_colors=args.k)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)

if __name__ == "__main__":
    main()
