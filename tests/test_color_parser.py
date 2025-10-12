"""Tests for color_parser module."""

import pytest
from src.color_parser import parse_color_from_css, blend_over, convert_hsl_to_rgb, parse_font_size_px, parse_style, RGBA


def test_hex6_parsing():
    """Test parsing 6-digit hex colors."""
    rgba = parse_color_from_css("#ff0000")
    assert rgba.r == 255
    assert rgba.g == 0
    assert rgba.b == 0
    assert rgba.a == 1.0


def test_hex8_parsing():
    """Test parsing 8-digit hex colors with alpha."""
    rgba = parse_color_from_css("#4FAEFF26")
    assert rgba.r == 79
    assert rgba.g == 174
    assert rgba.b == 255
    assert abs(rgba.a - 0.149) < 0.01  # 38/255 ≈ 0.149


def test_hex3_parsing():
    """Test parsing 3-digit hex colors."""
    rgba = parse_color_from_css("#f00")
    assert rgba.r == 255
    assert rgba.g == 0
    assert rgba.b == 0


def test_rgb_parsing():
    """Test parsing rgb() format."""
    rgba = parse_color_from_css("rgb(100, 150, 200)")
    assert rgba.r == 100
    assert rgba.g == 150
    assert rgba.b == 200
    assert rgba.a == 1.0


def test_rgba_parsing():
    """Test parsing rgba() format."""
    rgba = parse_color_from_css("rgba(100, 150, 200, 0.5)")
    assert rgba.r == 100
    assert rgba.g == 150
    assert rgba.b == 200
    assert rgba.a == 0.5


def test_hsl_to_rgb():
    """Test HSL to RGB conversion."""
    # Red: hsl(0, 100%, 50%)
    r, g, b = convert_hsl_to_rgb(0, 100, 50)
    assert r == 255
    assert g == 0
    assert b == 0

    # Gray: hsl(0, 0%, 50%)
    r, g, b = convert_hsl_to_rgb(0, 0, 50)
    assert r == g == b == 127


def test_hsl_parsing():
    """Test parsing hsl() format."""
    rgba = parse_color_from_css("hsl(0, 100%, 50%)")
    assert rgba.r == 255
    assert rgba.g == 0
    assert rgba.b == 0


def test_named_colors():
    """Test parsing named colors."""
    rgba = parse_color_from_css("white")
    assert rgba.to_rgb_tuple() == (255, 255, 255)

    rgba = parse_color_from_css("black")
    assert rgba.to_rgb_tuple() == (0, 0, 0)


def test_blend_over():
    """Test alpha blending."""
    # Semi-transparent blue over white
    over = RGBA(79, 174, 255, 0.149)
    under = (255, 255, 255)
    result = blend_over(over, under)

    # Expected: mix of blue and white
    assert result[0] < 255  # Some blue
    assert result[1] < 255  # Some blue
    assert result[2] == 255  # Fully blue channel


def test_parse_font_size_px():
    """Test font size parsing."""
    assert parse_font_size_px("16px") == 16.0
    assert parse_font_size_px("24px") == 24.0

    # pt to px (1pt ≈ 1.333px)
    assert abs(parse_font_size_px("12pt") - 16.0) < 0.1

    # em to px (assume 16px base)
    assert parse_font_size_px("1.5em") == 24.0


def test_parse_style():
    """Test CSS style string parsing."""
    style_str = "color: red; font-size: 16px; font-weight: bold"
    style_dict = parse_style(style_str)

    assert style_dict["color"] == "red"
    assert style_dict["font-size"] == "16px"
    assert style_dict["font-weight"] == "bold"
