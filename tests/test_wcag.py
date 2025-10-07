"""Tests for WCAG module."""

import pytest
from src.wcag import (
    relative_luminance,
    contrast_ratio,
    classify_wcag,
    suggest_fixes
)


def test_relative_luminance_black():
    """Test luminance of black."""
    lum = relative_luminance((0, 0, 0))
    assert abs(lum - 0.0) < 0.001


def test_relative_luminance_white():
    """Test luminance of white."""
    lum = relative_luminance((255, 255, 255))
    assert abs(lum - 1.0) < 0.001


def test_contrast_black_white():
    """Test contrast between black and white."""
    ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
    assert abs(ratio - 21.0) < 0.1


def test_contrast_same_color():
    """Test contrast of same color (should be 1:1)."""
    ratio = contrast_ratio((128, 128, 128), (128, 128, 128))
    assert abs(ratio - 1.0) < 0.1


def test_contrast_order_independent():
    """Test that contrast is independent of color order."""
    ratio1 = contrast_ratio((0, 0, 0), (255, 255, 255))
    ratio2 = contrast_ratio((255, 255, 255), (0, 0, 0))
    assert abs(ratio1 - ratio2) < 0.001


def test_classify_wcag_pass():
    """Test WCAG classification for passing contrast."""
    # High contrast should pass all levels
    wcag = classify_wcag(21.0, 16, 'normal')
    assert wcag['AA_normal'] == True
    assert wcag['AA_large'] == True
    assert wcag['AAA'] == True


def test_classify_wcag_fail():
    """Test WCAG classification for failing contrast."""
    # Low contrast should fail all levels
    wcag = classify_wcag(2.0, 16, 'normal')
    assert wcag['AA_normal'] == False
    assert wcag['AA_large'] == False
    assert wcag['AAA'] == False


def test_classify_wcag_large_text():
    """Test WCAG classification for large text."""
    # 3:1 passes for large text but not normal
    wcag = classify_wcag(3.5, 24, 'normal')  # 24px is large
    assert wcag['AA_normal'] == False
    assert wcag['AA_large'] == True
    assert wcag['is_large_text'] == True


def test_classify_wcag_bold_large():
    """Test WCAG classification for bold large text."""
    # 18.67px + bold qualifies as large text
    wcag = classify_wcag(3.5, 19, '700')
    assert wcag['AA_large'] == True
    assert wcag['is_large_text'] == True


def test_suggest_fixes_returns_suggestions():
    """Test that suggest_fixes returns suggestions for low contrast."""
    suggestions = suggest_fixes(
        contrast_ratio=2.0,
        text_rgb=(100, 100, 100),
        bg_rgb=(150, 150, 150),
        font_size_px=16,
        font_weight='normal'
    )

    assert len(suggestions) > 0
    assert all('type' in sug for sug in suggestions)
    assert all('description' in sug for sug in suggestions)
    assert all('new_value' in sug for sug in suggestions)


def test_suggest_fixes_empty_for_good_contrast():
    """Test that suggest_fixes returns empty for good contrast."""
    suggestions = suggest_fixes(
        contrast_ratio=7.0,  # Good contrast
        text_rgb=(0, 0, 0),
        bg_rgb=(255, 255, 255),
        font_size_px=16,
        font_weight='normal'
    )

    assert len(suggestions) == 0
