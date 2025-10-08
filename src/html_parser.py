"""HTML Parser for extracting text entities using BeautifulSoup."""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.color_parser import parse_style, parse_font_size_px


def extract_entities(content_html: str) -> List[Dict[str, Any]]:
    """
    Extract all text entities from HTML using BeautifulSoup.

    This function parses HTML content and extracts all <div> elements with
    id starting with "text-". It collects wrapper styles, span styles, and
    text content for each entity.

    Args:
        content_html: HTML content string

    Returns:
        List of dictionaries with entity data:
        - id: Entity ID
        - wrapper_style: Wrapper element style string
        - spans: List of span data (style, text)
        - text_content: Full text content
        - raw_html: Raw HTML of the entity

    Example:
        >>> html = '<div id="text-123"><span style="color: red;">Hello</span></div>'
        >>> entities = extract_entities(html)
        >>> entities[0]['id']
        'text-123'
    """
    soup = BeautifulSoup(content_html, "lxml")
    entities = []

    # Find all divs with id starting with "text-"
    for div in soup.find_all("div", id=re.compile(r"^text-")):
        entity_id = div.get("id")

        # Find wrapper with geometry (class contains "entity__wrapper" or "wrapper")
        wrapper = div.find(class_=re.compile(r"(entity__wrapper|wrapper)"))
        wrapper_style = wrapper.get("style", "") if wrapper else ""

        # Collect all spans with their styles and text
        spans = div.find_all("span")
        spans_data = []

        for span in spans:
            span_style = span.get("style", "")
            span_text = span.get_text(strip=False)

            if span_style or span_text:
                spans_data.append({"style": span_style, "text": span_text})

        # Extract all text for weighting
        text_content = div.get_text(strip=True)

        entities.append(
            {
                "id": entity_id,
                "wrapper_style": wrapper_style,
                "spans": spans_data,
                "text_content": text_content,
                "raw_html": str(div),
            }
        )

    return entities


def extract_font_info(
    entity: Dict[str, Any], default_size: float = 16.0, default_weight: str = "normal"
) -> Dict[str, Any]:
    """
    Extract font information from entity.

    Args:
        entity: Entity dictionary from extract_entities()
        default_size: Default font size in px
        default_weight: Default font weight

    Returns:
        Dictionary with:
        - size_px: Font size in pixels
        - weight: Font weight ('normal', 'bold', or numeric)
        - is_large: Whether font qualifies as "large text" per WCAG
    """
    # Check wrapper style for font properties
    wrapper_style = parse_style(entity.get("wrapper_style", ""))

    # Check first span if wrapper doesn't have font info
    spans = entity.get("spans", [])
    first_span_style = {}
    if spans:
        first_span_style = parse_style(spans[0].get("style", ""))

    # Get font size
    font_size_str = wrapper_style.get("font-size") or first_span_style.get("font-size")
    if font_size_str:
        size_px = parse_font_size_px(font_size_str) or default_size
    else:
        size_px = default_size

    # Get font weight
    font_weight = wrapper_style.get("font-weight") or first_span_style.get("font-weight") or default_weight

    # WCAG "large text" definition:
    # - 18pt (24px) and larger
    # - 14pt (18.67px) and larger if bold (weight >= 700)
    is_large = False
    if size_px >= 24:
        is_large = True
    elif size_px >= 18.67:
        # Check if bold
        if font_weight == "bold" or font_weight == "bolder":
            is_large = True
        elif font_weight.isdigit() and int(font_weight) >= 700:
            is_large = True

    return {"size_px": round(size_px, 2), "weight": font_weight, "is_large": is_large}


def extract_geometry(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract geometric information from entity wrapper.

    Parses CSS transform, width, height, top, left properties.

    Args:
        entity: Entity dictionary from extract_entities()

    Returns:
        Dictionary with geometric properties (can be empty if not found)
    """
    wrapper_style = parse_style(entity.get("wrapper_style", ""))

    geometry = {}

    # Parse dimensions
    if "width" in wrapper_style:
        width_str = wrapper_style["width"].replace("px", "").strip()
        try:
            geometry["width"] = float(width_str)
        except ValueError:
            pass

    if "height" in wrapper_style:
        height_str = wrapper_style["height"].replace("px", "").strip()
        try:
            geometry["height"] = float(height_str)
        except ValueError:
            pass

    # Parse position (top, left)
    if "top" in wrapper_style:
        top_str = wrapper_style["top"].replace("px", "").strip()
        try:
            geometry["top"] = float(top_str)
        except ValueError:
            pass

    if "left" in wrapper_style:
        left_str = wrapper_style["left"].replace("px", "").strip()
        try:
            geometry["left"] = float(left_str)
        except ValueError:
            pass

    # Parse transform (translate)
    if "transform" in wrapper_style:
        transform = wrapper_style["transform"]
        # Extract translate(x, y)
        translate_match = re.search(r"translate\s*\(\s*([\d.-]+)px\s*,\s*([\d.-]+)px\s*\)", transform)
        if translate_match:
            geometry["translate_x"] = float(translate_match.group(1))
            geometry["translate_y"] = float(translate_match.group(2))

    return geometry
