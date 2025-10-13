"""Tests for image analyzer module."""

import pytest
from PIL import Image
from src.image_analyzer import dominant_colors_mediancut, dominant_colors_kmeans, get_dominant_color_simple, analyze_image_region, DEFAULT_COLOR


@pytest.fixture
def test_image():
    """Create a simple test image."""
    # Create image with red and blue regions
    img = Image.new("RGB", (200, 200))
    pixels = img.load()

    for i in range(200):
        for j in range(200):
            if i < 100:
                pixels[i, j] = (255, 0, 0)  # Red
            else:
                pixels[i, j] = (0, 0, 255)  # Blue

    return img


@pytest.fixture
def single_color_image():
    """Create a single color test image."""
    img = Image.new("RGB", (100, 100), color=(0, 255, 0))  # Green
    return img


@pytest.fixture
def non_rgb_image():
    """Create a non-RGB image."""
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))  # Red with alpha
    return img


def test_dominant_colors_mediancut(test_image):
    """Test median-cut algorithm."""
    colors = dominant_colors_mediancut(test_image, k=2)

    assert len(colors) == 2
    assert all(isinstance(color, tuple) and len(color) == 2 for color in colors)

    # Check that we got RGB tuples and weights
    for rgb, weight in colors:
        assert len(rgb) == 3
        assert 0 <= weight <= 1


def test_dominant_colors_kmeans(test_image):
    """Test K-means algorithm."""
    colors = dominant_colors_kmeans(test_image, k=2)

    assert len(colors) == 2
    assert all(isinstance(color, tuple) and len(color) == 2 for color in colors)

    # Check RGB and weights
    for rgb, weight in colors:
        assert len(rgb) == 3
        assert 0 <= weight <= 1


def test_dominant_colors_sorted_by_weight(test_image):
    """Test that results are sorted by weight."""
    colors = dominant_colors_mediancut(test_image, k=3)

    weights = [weight for _, weight in colors]
    assert weights == sorted(weights, reverse=True)


def test_get_dominant_color_simple(test_image):
    """Test getting single dominant color."""
    rgb = get_dominant_color_simple(test_image, method="mediancut")

    assert len(rgb) == 3
    assert all(0 <= c <= 255 for c in rgb)


def test_dominant_colors_mediancut_with_bbox(test_image):
    """Test median-cut with bounding box."""
    # Crop to red region only (left half)
    bbox = (0, 0, 100, 200)
    colors = dominant_colors_mediancut(test_image, bbox=bbox, k=1)
    
    assert len(colors) == 1
    assert colors[0][0] == (255, 0, 0)  # Should be red
    assert colors[0][1] == 1.0


def test_dominant_colors_kmeans_with_single_color(single_color_image):
    """Test K-means with single color image."""
    colors = dominant_colors_kmeans(single_color_image, k=3)
    
    assert len(colors) == 1  # Should collapse to one color
    assert colors[0][0] == (0, 255, 0)  # Green
    assert colors[0][1] == 1.0


def test_dominant_colors_mediancut_non_rgb(non_rgb_image):
    """Test median-cut with non-RGB image."""
    colors = dominant_colors_mediancut(non_rgb_image, k=1)
    
    assert len(colors) == 1
    assert colors[0][0] == (255, 0, 0)  # Should convert to RGB and get red


def test_analyze_image_region(test_image):
    """Test analyze_image_region function."""
    geometry = {"left": 100, "top": 0, "width": 100, "height": 200}  # Blue region
    colors = analyze_image_region(test_image, geometry, method="kmeans", k=1)
    
    assert len(colors) == 1
    assert colors[0][0] == (0, 0, 255)  # Blue
    assert colors[0][1] == 1.0


def test_invalid_input_fallback(test_image):
    """Test fallback to default color on invalid input."""
    # Pass invalid image (not PIL Image)
    colors = dominant_colors_mediancut("invalid", k=5)
    
    assert len(colors) == 1
    assert colors[0][0] == DEFAULT_COLOR
    assert colors[0][1] == 1.0


def test_invalid_bbox_fallback(test_image):
    """Test fallback on invalid bbox."""
    bbox = (300, 300, 400, 400)  # Outside image bounds
    colors = dominant_colors_kmeans(test_image, bbox=bbox, k=5)
    
    assert len(colors) == 1
    assert colors[0][0] == DEFAULT_COLOR
    assert colors[0][1] == 1.0


def test_kmeans_reproducibility(test_image):
    """Test K-means reproducibility with random_state."""
    colors1 = dominant_colors_kmeans(test_image, k=2, random_state=42)
    colors2 = dominant_colors_kmeans(test_image, k=2, random_state=42)
    
    assert colors1 == colors2


def test_get_dominant_color_simple_kmeans(test_image):
    """Test get_dominant_color_simple with kmeans method."""
    rgb = get_dominant_color_simple(test_image, method="kmeans")
    
    assert len(rgb) == 3
    assert all(0 <= c <= 255 for c in rgb)


def test_analyze_image_region_invalid_geometry(test_image):
    """Test analyze_image_region with invalid geometry."""
    geometry = "invalid"  # Not a dict
    colors = analyze_image_region(test_image, geometry)
    
    assert len(colors) == 1
    assert colors[0][0] == DEFAULT_COLOR
    assert colors[0][1] == 1.0


def test_dominant_colors_mediancut_k_greater_than_colors(test_image):
    """Test median-cut with k greater than actual colors."""
    colors = dominant_colors_mediancut(test_image, k=10)
    
    assert len(colors) <= 10  # Should not exceed actual unique colors
    assert sum(weight for _, weight in colors) == pytest.approx(1.0)