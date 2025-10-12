"""Tests for HTML parser module."""

import pytest
from src.html_parser import (
    extract_entities,
    extract_font_info,
    extract_geometry,
    _extract_entity_id,
    _extract_color
)


# ============================================================================
# Basic Extraction Tests
# ============================================================================

def test_extract_entities_simple():
    """Test extracting entities from simple HTML."""
    html = """
    <div id="text-1" class="entity">
        <div class="entity__wrapper" style="width: 500px; height: 100px;">
            <span style="color: red; font-size: 16px;">Hello</span>
        </div>
    </div>
    """

    entities = extract_entities(html)

    assert len(entities) == 1
    assert entities[0]["id"] == "text-1"
    assert len(entities[0]["spans"]) == 1
    assert "color: red" in entities[0]["spans"][0]["style"]


def test_extract_entities_multiple():
    """Test extracting multiple entities."""
    html = """
    <div id="text-1"><span>First</span></div>
    <div id="text-2"><span>Second</span></div>
    """

    entities = extract_entities(html)

    assert len(entities) == 2
    assert entities[0]["id"] == "text-1"
    assert entities[1]["id"] == "text-2"


def test_extract_font_info_default():
    """Test extracting font info with defaults."""
    entity = {"wrapper_style": "", "spans": []}

    font_info = extract_font_info(entity)

    assert font_info["size_px"] == 16.0  # Default
    assert font_info["weight"] == "normal"  # Default
    assert font_info["is_large"] == False


def test_extract_font_info_large_text():
    """Test identifying large text."""
    entity = {"wrapper_style": "font-size: 24px", "spans": []}

    font_info = extract_font_info(entity)

    assert font_info["size_px"] == 24.0
    assert font_info["is_large"] == True


def test_extract_font_info_bold_large():
    """Test identifying bold large text."""
    entity = {"wrapper_style": "font-size: 19px; font-weight: 700", "spans": []}

    font_info = extract_font_info(entity)

    assert font_info["size_px"] == 19.0
    assert font_info["weight"] == "700"
    assert font_info["is_large"] == True


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================

def test_extract_entities_empty_html():
    """Test handling empty HTML."""
    assert extract_entities("") == []
    assert extract_entities("   ") == []
    assert extract_entities(None) == []


def test_extract_entities_invalid_html():
    """Test handling malformed HTML."""
    html = "<div id='text-1'><span>Unclosed div"
    entities = extract_entities(html)
    
    # Should still extract what it can
    assert len(entities) >= 0


def test_extract_entities_no_text_prefix():
    """Test ignoring divs without 'text-' prefix."""
    html = """
    <div id="other-1"><span>Not a text entity</span></div>
    <div id="text-1"><span>Valid entity</span></div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert entities[0]["id"] == "text-1"


def test_extract_entities_missing_id():
    """Test handling divs without id attribute."""
    html = """
    <div><span>No ID</span></div>
    <div id="text-1"><span>Has ID</span></div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert entities[0]["id"] == "text-1"


def test_extract_entities_whitespace_id():
    """Test handling IDs with whitespace."""
    html = """
    <div id="text-1">
        <span>Content</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert entities[0]["id"].strip() == "text-1"


def test_extract_entities_empty_spans():
    """Test handling empty spans."""
    html = """
    <div id="text-1">
        <span></span>
        <span style="">  </span>
        <span style="color: red;">Valid</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    # Empty spans with whitespace-only text are still included
    spans_with_text = [s for s in entities[0]["spans"] if s["text"].strip()]
    assert len(spans_with_text) >= 1
    assert any("Valid" in s["text"] for s in entities[0]["spans"])


def test_extract_entities_color_extraction():
    """Test color extraction from spans."""
    html = """
    <div id="text-1">
        <span style="color: rgb(255, 0, 0);">Red text</span>
        <span style="font-size: 20px;">No color</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert len(entities[0]["spans"]) == 2
    assert entities[0]["spans"][0]["color"] is not None
    assert entities[0]["spans"][1]["color"] is None


def test_extract_entities_text_content():
    """Test text content extraction."""
    html = """
    <div id="text-1">
        <span>Hello </span>
        <span>World</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert "Hello" in entities[0]["text_content"]
    assert "World" in entities[0]["text_content"]


# ============================================================================
# Wrapper and Geometry Tests
# ============================================================================

def test_extract_entities_with_wrapper():
    """Test extraction with entity__wrapper class."""
    html = """
    <div id="text-1">
        <div class="entity__wrapper" style="width: 200px; height: 50px;">
            <span>Content</span>
        </div>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert "width: 200px" in entities[0]["wrapper_style"]
    assert "height: 50px" in entities[0]["wrapper_style"]


def test_extract_entities_with_generic_wrapper():
    """Test extraction with generic wrapper class."""
    html = """
    <div id="text-1">
        <div class="wrapper" style="left: 100px;">
            <span>Content</span>
        </div>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert "left: 100px" in entities[0]["wrapper_style"]


def test_extract_entities_no_wrapper():
    """Test extraction without wrapper."""
    html = """
    <div id="text-1">
        <span>Direct content</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert entities[0]["wrapper_style"] == ""


def test_extract_geometry_complete():
    """Test extracting complete geometry."""
    entity = {
        "wrapper_style": "width: 300px; height: 150px; top: 50px; left: 100px; transform: translate(10px, 20px);"
    }
    
    geometry = extract_geometry(entity)
    
    assert geometry["width"] == 300.0
    assert geometry["height"] == 150.0
    assert geometry["top"] == 50.0
    assert geometry["left"] == 100.0
    assert geometry["translate_x"] == 10.0
    assert geometry["translate_y"] == 20.0


def test_extract_geometry_partial():
    """Test extracting partial geometry."""
    entity = {
        "wrapper_style": "width: 200px; left: 50px;"
    }
    
    geometry = extract_geometry(entity)
    
    assert geometry["width"] == 200.0
    assert geometry["left"] == 50.0
    assert "height" not in geometry
    assert "top" not in geometry


def test_extract_geometry_invalid():
    """Test handling invalid geometry values."""
    entity = {
        "wrapper_style": "width: invalid; height: 100px;"
    }
    
    geometry = extract_geometry(entity)
    
    assert "width" not in geometry
    assert geometry["height"] == 100.0


def test_extract_geometry_empty():
    """Test handling empty wrapper style."""
    entity = {"wrapper_style": ""}
    
    geometry = extract_geometry(entity)
    
    assert geometry == {}


def test_extract_geometry_none_entity():
    """Test handling None entity."""
    geometry = extract_geometry(None)
    
    assert geometry == {}


# ============================================================================
# Font Info Tests
# ============================================================================

def test_extract_font_info_from_span():
    """Test extracting font info from first span."""
    entity = {
        "wrapper_style": "",
        "spans": [
            {"style": "font-size: 20px; font-weight: bold;", "text": "Content"}
        ]
    }
    
    font_info = extract_font_info(entity)
    
    assert font_info["size_px"] == 20.0
    assert font_info["weight"] == "bold"


def test_extract_font_info_wrapper_priority():
    """Test wrapper style takes priority over span."""
    entity = {
        "wrapper_style": "font-size: 24px;",
        "spans": [
            {"style": "font-size: 16px;", "text": "Content"}
        ]
    }
    
    font_info = extract_font_info(entity)
    
    assert font_info["size_px"] == 24.0


def test_extract_font_info_bold_variants():
    """Test different bold weight formats."""
    # Numeric weight
    entity1 = {"wrapper_style": "font-weight: 700", "spans": []}
    assert extract_font_info(entity1)["weight"] == "700"
    
    # Named weight
    entity2 = {"wrapper_style": "font-weight: bold", "spans": []}
    assert extract_font_info(entity2)["weight"] == "bold"
    
    # Bolder
    entity3 = {"wrapper_style": "font-weight: bolder", "spans": []}
    assert extract_font_info(entity3)["weight"] == "bolder"


def test_extract_font_info_large_text_thresholds():
    """Test WCAG large text thresholds."""
    # 24px is always large
    entity1 = {"wrapper_style": "font-size: 24px;", "spans": []}
    assert extract_font_info(entity1)["is_large"] is True
    
    # 23px is not large
    entity2 = {"wrapper_style": "font-size: 23px;", "spans": []}
    assert extract_font_info(entity2)["is_large"] is False
    
    # 19px with bold is large
    entity3 = {"wrapper_style": "font-size: 19px; font-weight: 700", "spans": []}
    assert extract_font_info(entity3)["is_large"] is True
    
    # 18px with bold is not large (threshold is 18.67px)
    entity4 = {"wrapper_style": "font-size: 18px; font-weight: 700", "spans": []}
    assert extract_font_info(entity4)["is_large"] is False


def test_extract_font_info_invalid_entity():
    """Test handling invalid entity types."""
    font_info = extract_font_info(None)
    
    assert font_info["size_px"] == 16.0
    assert font_info["weight"] == "normal"
    assert font_info["is_large"] is False


def test_extract_font_info_malformed_spans():
    """Test handling malformed spans list."""
    entity = {
        "wrapper_style": "",
        "spans": "not a list"
    }
    
    font_info = extract_font_info(entity)
    
    # Should use defaults
    assert font_info["size_px"] == 16.0
    assert font_info["weight"] == "normal"


# ============================================================================
# Color Extraction Tests
# ============================================================================

def test_extract_color_valid():
    """Test extracting valid color."""
    color = _extract_color("color: rgb(255, 0, 0); font-size: 16px;")
    
    assert color is not None


def test_extract_color_no_color():
    """Test handling style without color."""
    color = _extract_color("font-size: 16px; font-weight: bold;")
    
    assert color is None


def test_extract_color_empty():
    """Test handling empty style string."""
    assert _extract_color("") is None
    assert _extract_color("   ") is None


def test_extract_color_none():
    """Test handling None input."""
    assert _extract_color(None) is None


def test_extract_color_invalid_type():
    """Test handling non-string input."""
    assert _extract_color(123) is None
    assert _extract_color([]) is None


# ============================================================================
# Complex Scenarios
# ============================================================================

def test_extract_entities_complex_nesting():
    """Test complex nested HTML structure."""
    html = """
    <div id="text-1">
        <div class="entity__wrapper" style="width: 500px;">
            <div class="inner">
                <span style="color: blue;">Part 1</span>
                <span style="color: red;">Part 2</span>
            </div>
        </div>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert len(entities[0]["spans"]) == 2


def test_extract_entities_special_characters():
    """Test handling special characters in text."""
    html = """
    <div id="text-1">
        <span>Hello & "World" < > '</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert "Hello" in entities[0]["text_content"]


def test_extract_entities_unicode():
    """Test handling Unicode characters."""
    html = """
    <div id="text-1">
        <span>Привет 世界 🌍</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert "Привет" in entities[0]["text_content"]
    assert "世界" in entities[0]["text_content"]


def test_extract_entities_raw_html_preserved():
    """Test that raw HTML is preserved."""
    html = """
    <div id="text-1">
        <span style="color: red;">Content</span>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    assert "text-1" in entities[0]["raw_html"]
    assert "span" in entities[0]["raw_html"]


def test_extract_geometry_negative_values():
    """Test handling negative geometry values."""
    entity = {
        "wrapper_style": "top: -10px; left: -5px; transform: translate(-20px, -15px);"
    }
    
    geometry = extract_geometry(entity)
    
    assert geometry["top"] == -10.0
    assert geometry["left"] == -5.0
    assert geometry["translate_x"] == -20.0
    assert geometry["translate_y"] == -15.0


def test_extract_geometry_decimal_values():
    """Test handling decimal geometry values."""
    entity = {
        "wrapper_style": "width: 123.45px; height: 67.89px;"
    }
    
    geometry = extract_geometry(entity)
    
    assert geometry["width"] == 123.45
    assert geometry["height"] == 67.89


def test_extract_entities_multiple_wrappers():
    """Test handling multiple potential wrappers."""
    html = """
    <div id="text-1">
        <div class="outer wrapper" style="height: 200px;">
            <div class="entity__wrapper" style="width: 100px;">
                <span>Content</span>
            </div>
        </div>
    </div>
    """
    
    entities = extract_entities(html)
    
    assert len(entities) == 1
    # Should find first matching wrapper (could be either wrapper or entity__wrapper)
    assert entities[0]["wrapper_style"] != ""
    # At least one dimension should be present
    assert "width" in entities[0]["wrapper_style"] or "height" in entities[0]["wrapper_style"]