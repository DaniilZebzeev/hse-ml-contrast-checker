"""Main Contrast Checker Module - Orchestrates all analysis."""

import json
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from PIL import Image

from src.color_parser import parse_color_from_css, blend_over, parse_style, RGBA
from src.html_parser import extract_entities, extract_font_info, extract_geometry
from src.image_analyzer import analyze_image_region, get_dominant_color_simple
from src.wcag import compute_contrast_ratio, classify_contrast_level, suggest_contrast_fixes


def analyze_text_colors(spans_data: List[Dict], default_color: str) -> List[Tuple[Tuple[int, int, int], str, float]]:
    """
    Analyze text colors with font-size and text-length weighting.

    Args:
        spans_data: List of span dictionaries with 'style' and 'text'
        default_color: Default color if no color specified

    Returns:
        List of (rgb_tuple, css_color, weight) sorted by weight
    """
    if not spans_data:
        rgba = parse_color_from_css(default_color)
        return [(rgba.to_rgb_tuple(), default_color, 1.0)]

    weighted_colors = []

    for span in spans_data:
        style = parse_style(span.get("style", ""))

        # Extract color
        color_css = style.get("color", default_color)
        rgba = parse_color_from_css(color_css)

        # Extract font size (for weighting)
        font_size_str = style.get("font-size", "16px")
        try:
            from src.color_parser import parse_font_size_px

            font_size = parse_font_size_px(font_size_str) or 16.0
        except:
            font_size = 16.0

        # Text length
        text_len = len(span.get("text", ""))

        # Weight = visual area (font_size × text_length)
        weight = font_size * text_len

        weighted_colors.append((rgba.to_rgb_tuple(), color_css, weight))

    # Normalize weights
    total_weight = sum(w for _, _, w in weighted_colors)
    if total_weight > 0:
        weighted_colors = [(rgb, css, w / total_weight) for rgb, css, w in weighted_colors]

    # Sort by weight descending
    weighted_colors.sort(key=lambda x: x[2], reverse=True)

    return weighted_colors


def determine_effective_background(
    slide_data: Dict[str, Any], bg_image: Optional[Image.Image] = None, ml_method: str = "mediancut", k_colors: int = 5
) -> Tuple[Tuple[int, int, int], str, Any]:
    """
    Determine effective background color.

    Priority:
    1. If bg_image provided and entity has geometry -> analyze image region
    2. If slide has base_color -> use that
    3. Fallback: white

    Args:
        slide_data: Slide JSON data
        bg_image: Optional background image
        ml_method: 'mediancut' or 'kmeans'
        k_colors: Number of dominant colors to extract

    Returns:
        Tuple of (rgb, source_description, details)
    """
    # Check for base_color
    base_color = slide_data.get("base_color")

    if base_color:
        rgba = parse_color_from_css(base_color)
        # If semi-transparent, blend over white
        if rgba.a < 1.0:
            rgb = blend_over(rgba, (255, 255, 255))
            return (rgb, f"base_color blended: {base_color}", {"original": base_color, "blended": rgb})
        else:
            return (rgba.to_rgb_tuple(), f"base_color: {base_color}", {"color": base_color})

    # Check for background image
    if bg_image:
        dominant = get_dominant_color_simple(bg_image, method=ml_method)
        return (dominant, f"image dominant ({ml_method})", {"method": ml_method})

    # Fallback: white
    return ((255, 255, 255), "default: white", {})


def analyze_entity_contrast(
    entity: Dict[str, Any], effective_bg: Tuple[int, int, int], default_text_color: str = "#000000"
) -> Dict[str, Any]:
    """
    Analyze contrast for a single entity.

    Args:
        entity: Entity dictionary from extract_entities
        effective_bg: Effective background RGB
        default_text_color: Default text color

    Returns:
        Dictionary with contrast analysis results
    """
    # Extract font info
    font_info = extract_font_info(entity)

    # Extract text colors with weighting
    text_colors = analyze_text_colors(entity.get("spans", []), default_text_color)

    # Calculate contrast for each text color
    contrasts: List[Dict[str, Any]] = []
    for rgb, css, weight in text_colors:
        ratio = compute_contrast_ratio(rgb, effective_bg)
        wcag = classify_contrast_level(ratio, font_info["size_px"], font_info["weight"])

        contrasts.append({"rgb": rgb, "css": css, "weight": weight, "ratio": round(ratio, 2), "wcag": wcag})

    # Find minimum ratio (worst case)
    ratios: List[float] = [float(c["ratio"]) for c in contrasts]
    min_ratio = min(ratios)
    min_contrast = next(c for c in contrasts if c["ratio"] == min_ratio)

    # Overall WCAG classification (based on worst case)
    overall_wcag: Dict[str, Any] = min_contrast["wcag"]  # type: ignore
    min_text_rgb: Tuple[int, int, int] = min_contrast["rgb"]  # type: ignore

    # Generate suggestions if fails AA normal
    suggestions: List[Dict[str, Any]] = []
    if not overall_wcag["AA_normal"]:
        suggestions = suggest_contrast_fixes(min_ratio, min_text_rgb, effective_bg, font_info["size_px"], font_info["weight"])

    return {
        "id": entity["id"],
        "text_colors": [{"rgb": c["rgb"], "css": c["css"], "weight": c["weight"]} for c in contrasts],
        "contrast": {
            "min_ratio": min_ratio,
            "max_ratio": round(max(ratios), 2),
            "wcag": overall_wcag,
            "contrasts": contrasts,
        },
        "font": font_info,
        "suggestions": suggestions,
    }


def analyze_slide(
    slide_json_path: str,
    slide_index: Optional[int] = None,
    bg_image_path: Optional[str] = None,
    ml_method: str = "mediancut",
    k_colors: int = 5,
) -> Dict[str, Any]:
    """
    Analyze contrast for a slide.

    Args:
        slide_json_path: Path to slide JSON file
        slide_index: If JSON is array, index of slide (None = first slide or single object)
        bg_image_path: Optional path to background image
        ml_method: 'mediancut' or 'kmeans'
        k_colors: Number of dominant colors to extract

    Returns:
        Analysis results dictionary

    Raises:
        FileNotFoundError: If files not found
        ValueError: If JSON is invalid
    """
    # Load slide JSON
    with open(slide_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle array vs single object
    if isinstance(data, list):
        if slide_index is not None:
            slide_data = data[slide_index]
        else:
            slide_data = data[0]
    else:
        slide_data = data

    # Load background image if provided
    bg_image = None
    if bg_image_path:
        bg_image = Image.open(bg_image_path).convert("RGB")

    # Determine effective background
    effective_bg, bg_source, bg_details = determine_effective_background(slide_data, bg_image, ml_method, k_colors)

    # Extract entities from HTML
    content_html = slide_data.get("content_html", "")
    entities = extract_entities(content_html)

    # Analyze each entity
    entity_results = []
    for entity in entities:
        result = analyze_entity_contrast(entity, effective_bg)
        entity_results.append(result)

    # Build final result
    result = {
        "slide_id": slide_data.get("id", "unknown"),
        "background": {"effective_rgb": effective_bg, "source": bg_source, "details": bg_details},
        "ml_method": ml_method,
        "entities": entity_results,
        "summary": {
            "total_entities": len(entity_results),
            "passed_AA_normal": sum(1 for e in entity_results if e["contrast"]["wcag"]["AA_normal"]),
            "failed_AA_normal": sum(1 for e in entity_results if not e["contrast"]["wcag"]["AA_normal"]),
        },
    }

    return result
