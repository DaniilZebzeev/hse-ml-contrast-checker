"""Image Analyzer for extracting dominant colors using ML algorithms.

Implements two unsupervised learning methods:
1. Median-cut algorithm (via Pillow's ADAPTIVE palette)
2. K-means clustering (via scikit-learn)
"""

from typing import List, Tuple, Optional
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


def dominant_colors_mediancut(
    img: Image.Image, bbox: Optional[Tuple[int, int, int, int]] = None, k: int = 5
) -> List[Tuple[Tuple[int, int, int], float]]:
    """
    Extract dominant colors using Median-cut algorithm.

    Median-cut is a classic unsupervised learning algorithm for palette quantization.
    It recursively divides the color space by the median value of the dimension
    with the largest range.

    This method is faster but may be less accurate for complex images compared to K-means.

    Args:
        img: PIL Image object (RGB mode)
        bbox: Optional bounding box (left, top, right, bottom) to crop
        k: Number of dominant colors to extract

    Returns:
        List of tuples: ((r, g, b), weight)
        Sorted by weight (descending)

    Example:
        >>> img = Image.open('background.png')
        >>> colors = dominant_colors_mediancut(img, k=5)
        >>> colors[0]  # Most dominant color
        ((245, 123, 67), 0.42)
    """
    # Crop region if bbox provided
    if bbox:
        region = img.crop(bbox)
    else:
        region = img.copy()

    # Convert to RGB if needed
    if region.mode != "RGB":
        region = region.convert("RGB")

    # Resize for performance (max 150x150)
    max_size = 150
    if region.width > max_size or region.height > max_size:
        aspect_ratio = region.width / region.height
        if aspect_ratio > 1:
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:
            new_height = max_size
            new_width = int(max_size * aspect_ratio)
        region = region.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Median-cut quantization (ADAPTIVE palette)
    # This is the ML algorithm - it learns the optimal palette from the image
    pal_img = region.convert("P", palette=Image.Palette.ADAPTIVE, colors=k)

    # Get palette and color counts
    palette = pal_img.getpalette()  # [r1, g1, b1, r2, g2, b2, ...]
    color_counts = pal_img.getcolors()  # [(count1, idx1), (count2, idx2), ...]

    if not color_counts or not palette:
        # Fallback: return dominant color
        return [((128, 128, 128), 1.0)]

    # Convert to list of ((r, g, b), weight)
    total_pixels = sum(count for count, _ in color_counts)
    result = []

    for count, idx in color_counts:
        # idx is the palette index (integer)
        assert isinstance(idx, int), "Expected idx to be int"
        r = palette[idx * 3]
        g = palette[idx * 3 + 1]
        b = palette[idx * 3 + 2]
        weight = count / total_pixels
        result.append(((r, g, b), weight))

    # Sort by weight (descending)
    result.sort(key=lambda x: x[1], reverse=True)

    return result[:k]


def dominant_colors_kmeans(
    img: Image.Image, bbox: Optional[Tuple[int, int, int, int]] = None, k: int = 5, random_state: int = 42
) -> List[Tuple[Tuple[int, int, int], float]]:
    """
    Extract dominant colors using K-means clustering.

    K-means is a standard unsupervised machine learning algorithm that partitions
    pixels into k clusters by minimizing within-cluster variance. Each cluster
    center represents a dominant color.

    This method is more accurate for complex images but slower than median-cut.

    Args:
        img: PIL Image object (RGB mode)
        bbox: Optional bounding box (left, top, right, bottom) to crop
        k: Number of clusters (dominant colors)
        random_state: Random seed for reproducibility

    Returns:
        List of tuples: ((r, g, b), weight)
        Sorted by weight (descending)

    Example:
        >>> img = Image.open('background.png')
        >>> colors = dominant_colors_kmeans(img, k=5)
        >>> colors[0]  # Most dominant color
        ((242, 118, 71), 0.38)
    """
    # Crop region if bbox provided
    if bbox:
        region = img.crop(bbox)
    else:
        region = img.copy()

    # Convert to RGB if needed
    if region.mode != "RGB":
        region = region.convert("RGB")

    # Resize for performance (150x150)
    region = region.resize((150, 150), Image.Resampling.LANCZOS)

    # Convert to numpy array and reshape to pixels
    pixels = np.array(region).reshape(-1, 3)

    # K-means clustering - this is the ML algorithm
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    kmeans.fit(pixels)

    # Get cluster centers (dominant colors) and labels
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_

    # Calculate weights (proportion of pixels in each cluster)
    counts = np.bincount(labels)
    weights = counts / len(labels)

    # Build result list
    result = [(tuple(colors[i]), weights[i]) for i in range(k)]

    # Sort by weight (descending)
    result.sort(key=lambda x: x[1], reverse=True)

    return result


def get_dominant_color_simple(img: Image.Image, method: str = "mediancut") -> Tuple[int, int, int]:
    """
    Get single most dominant color from image.

    Args:
        img: PIL Image object
        method: 'mediancut' or 'kmeans'

    Returns:
        RGB tuple of most dominant color
    """
    if method == "kmeans":
        colors = dominant_colors_kmeans(img, k=1)
    else:
        colors = dominant_colors_mediancut(img, k=1)

    if colors:
        return colors[0][0]

    # Fallback
    return (128, 128, 128)


def analyze_image_region(
    img: Image.Image, geometry: dict, method: str = "mediancut", k: int = 5
) -> List[Tuple[Tuple[int, int, int], float]]:
    """
    Analyze image region based on entity geometry.

    Args:
        img: PIL Image object
        geometry: Dictionary with 'left', 'top', 'width', 'height'
        method: 'mediancut' or 'kmeans'
        k: Number of dominant colors

    Returns:
        List of dominant colors with weights
    """
    # Extract bounding box
    left = geometry.get("left", 0)
    top = geometry.get("top", 0)
    width = geometry.get("width", img.width)
    height = geometry.get("height", img.height)

    # Include translate if present
    left += geometry.get("translate_x", 0)
    top += geometry.get("translate_y", 0)

    # Ensure within image bounds
    left = max(0, min(left, img.width))
    top = max(0, min(top, img.height))
    right = max(0, min(left + width, img.width))
    bottom = max(0, min(top + height, img.height))

    bbox = (int(left), int(top), int(right), int(bottom))

    # Extract dominant colors
    if method == "kmeans":
        return dominant_colors_kmeans(img, bbox=bbox, k=k)
    else:
        return dominant_colors_mediancut(img, bbox=bbox, k=k)
