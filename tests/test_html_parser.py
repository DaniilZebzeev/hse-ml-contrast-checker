"""Tests for HTML parser module."""

import pytest
from src.html_parser import extract_entities, extract_font_info


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
