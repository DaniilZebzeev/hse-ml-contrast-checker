"""Tests for image analyzer module."""

import pytest
from PIL import Image
from src.image_analyzer import (
    dominant_colors_mediancut,
    dominant_colors_kmeans,
    get_dominant_color_simple
)


@pytest.fixture
def test_image():
    """Create a simple test image."""
    # Create image with red and blue regions
    img = Image.new('RGB', (200, 200))
    pixels = img.load()

    for i in range(200):
        for j in range(200):
            if i < 100:
                pixels[i, j] = (255, 0, 0)  # Red
            else:
                pixels[i, j] = (0, 0, 255)  # Blue

    return img


def test_dominant_colors_mediancut(test_image):
    """Test median-cut algorithm."""
    colors = dominant_colors_mediancut(test_image, k=2)

    assert len(colors) == 2
    assert all(isinstance(color, tuple) and len(color) == 2 for color in colors)

    # Check that we got RGB tuples and weights
    for (rgb, weight) in colors:
        assert len(rgb) == 3
        assert 0 <= weight <= 1


def test_dominant_colors_kmeans(test_image):
    """Test K-means algorithm."""
    colors = dominant_colors_kmeans(test_image, k=2)

    assert len(colors) == 2
    assert all(isinstance(color, tuple) and len(color) == 2 for color in colors)

    # Check RGB and weights
    for (rgb, weight) in colors:
        assert len(rgb) == 3
        assert 0 <= weight <= 1


def test_dominant_colors_sorted_by_weight(test_image):
    """Test that results are sorted by weight."""
    colors = dominant_colors_mediancut(test_image, k=3)

    weights = [weight for _, weight in colors]
    assert weights == sorted(weights, reverse=True)


def test_get_dominant_color_simple(test_image):
    """Test getting single dominant color."""
    rgb = get_dominant_color_simple(test_image, method='mediancut')

    assert len(rgb) == 3
    assert all(0 <= c <= 255 for c in rgb)
