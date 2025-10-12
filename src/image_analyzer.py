"""Image Analyzer for extracting dominant colors using ML algorithms.

Implements two unsupervised learning methods:
1. Median-cut algorithm (via Pillow's ADAPTIVE palette)
2. K-means clustering (via scikit-learn)
"""

from typing import List, Tuple, Optional
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


# Default fallback color (neutral gray)
DEFAULT_COLOR = (128, 128, 128)


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
    try:
        # Validate input
        if not isinstance(img, Image.Image):
            return [(DEFAULT_COLOR, 1.0)]
        
        if k < 1:
            k = 1

        # Crop region if bbox provided
        if bbox:
            region = _safe_crop(img, bbox)
        else:
            region = img.copy()

        if region.width == 0 or region.height == 0:
            return [(DEFAULT_COLOR, 1.0)]

        # Convert to RGB if needed
        if region.mode != "RGB":
            region = region.convert("RGB")

        # Resize for performance (max 150x150)
        region = _safe_resize(region, max_size=150)

        # Median-cut quantization (ADAPTIVE palette)
        # This is the ML algorithm - it learns the optimal palette from the image
        pal_img = region.convert("P", palette=Image.Palette.ADAPTIVE, colors=k)

        # Get palette and color counts
        palette = pal_img.getpalette()  # [r1, g1, b1, r2, g2, b2, ...]
        color_counts = pal_img.getcolors()  # [(count1, idx1), (count2, idx2), ...]

        if not color_counts or not palette:
            # Fallback: return default color
            return [(DEFAULT_COLOR, 1.0)]

        # Convert to list of ((r, g, b), weight)
        total_pixels = sum(count for count, _ in color_counts)
        if total_pixels == 0:
            return [(DEFAULT_COLOR, 1.0)]

        result = []

        for count, idx in color_counts:
            # idx is the palette index (integer)
            if not isinstance(idx, int) or idx < 0:
                continue
            
            palette_idx = idx * 3
            if palette_idx + 2 >= len(palette):
                continue

            r = palette[palette_idx]
            g = palette[palette_idx + 1]
            b = palette[palette_idx + 2]
            weight = count / total_pixels
            result.append(((int(r), int(g), int(b)), float(weight)))

        # Sort by weight (descending)
        result.sort(key=lambda x: x[1], reverse=True)

        return result[:k] if result else [(DEFAULT_COLOR, 1.0)]

    except Exception:
        # Return default color on any error
        return [(DEFAULT_COLOR, 1.0)]


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
    try:
        # Validate input
        if not isinstance(img, Image.Image):
            return [(DEFAULT_COLOR, 1.0)]
        
        if k < 1:
            k = 1

        # Crop region if bbox provided
        if bbox:
            region = _safe_crop(img, bbox)
        else:
            region = img.copy()

        if region.width == 0 or region.height == 0:
            return [(DEFAULT_COLOR, 1.0)]

        # Convert to RGB if needed
        if region.mode != "RGB":
            region = region.convert("RGB")

        # Resize for performance (150x150)
        region = region.resize((150, 150), Image.Resampling.LANCZOS)

        # Convert to numpy array and reshape to pixels
        pixels = np.array(region).reshape(-1, 3)

        if len(pixels) == 0:
            return [(DEFAULT_COLOR, 1.0)]

        # Check number of unique pixels to avoid issues with KMeans
        unique_pixels = np.unique(pixels, axis=0)
        k = min(k, len(unique_pixels))

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
        result = [
            (tuple(int(c) for c in colors[i]), float(weights[i])) 
            for i in range(len(colors))
        ]

        # Filter out zero-weight clusters (in case)
        result = [item for item in result if item[1] > 0]

        # Sort by weight (descending)
        result.sort(key=lambda x: x[1], reverse=True)

        return result if result else [(DEFAULT_COLOR, 1.0)]

    except Exception:
        # Return default color on any error
        return [(DEFAULT_COLOR, 1.0)]


def get_dominant_color_simple(img: Image.Image, method: str = "mediancut") -> Tuple[int, int, int]:
    """
    Get single most dominant color from image.

    Args:
        img: PIL Image object
        method: 'mediancut' or 'kmeans'

    Returns:
        RGB tuple of most dominant color
    """
    try:
        if not isinstance(img, Image.Image):
            return DEFAULT_COLOR

        if method == "kmeans":
            colors = dominant_colors_kmeans(img, k=1)
        else:
            colors = dominant_colors_mediancut(img, k=1)

        if colors and len(colors) > 0:
            return colors[0][0]

    except Exception:
        pass

    # Fallback
    return DEFAULT_COLOR


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
    try:
        if not isinstance(img, Image.Image):
            return [(DEFAULT_COLOR, 1.0)]

        if not isinstance(geometry, dict):
            return [(DEFAULT_COLOR, 1.0)]

        # Extract bounding box with safe defaults
        bbox = _extract_bbox_from_geometry(img, geometry)

        # Validate bbox
        if not _is_valid_bbox(bbox):
            return [(DEFAULT_COLOR, 1.0)]

        # Extract dominant colors
        if method == "kmeans":
            return dominant_colors_kmeans(img, bbox=bbox, k=k)
        else:
            return dominant_colors_mediancut(img, bbox=bbox, k=k)

    except Exception:
        return [(DEFAULT_COLOR, 1.0)]


def _safe_crop(img: Image.Image, bbox: Tuple[int, int, int, int]) -> Image.Image:
    """
    Safely crop image with bounds validation.
    
    Args:
        img: PIL Image object
        bbox: (left, top, right, bottom)
        
    Returns:
        Cropped image or empty image if crop invalid
    """
    try:
        left, top, right, bottom = bbox
        
        # Ensure values are within bounds
        left = max(0, min(left, img.width))
        top = max(0, min(top, img.height))
        right = max(left, min(right, img.width))
        bottom = max(top, min(bottom, img.height))
        
        return img.crop((left, top, right, bottom))
    except Exception:
        return Image.new("RGB", (0, 0))


def _safe_resize(img: Image.Image, max_size: int = 150) -> Image.Image:
    """
    Safely resize image maintaining aspect ratio.
    
    Args:
        img: PIL Image object
        max_size: Maximum dimension size
        
    Returns:
        Resized image or original if resize fails
    """
    try:
        if img.width == 0 or img.height == 0:
            return img
        
        if img.width <= max_size and img.height <= max_size:
            return img
        
        aspect_ratio = img.width / img.height
        if aspect_ratio > 1:
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:
            new_height = max_size
            new_width = int(max_size * aspect_ratio)
        
        # Ensure dimensions are at least 1
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    except Exception:
        return img


def _extract_bbox_from_geometry(img: Image.Image, geometry: dict) -> Tuple[int, int, int, int]:
    """
    Extract and validate bounding box from geometry dictionary.
    
    Args:
        img: PIL Image object
        geometry: Dictionary with positional data
        
    Returns:
        Tuple (left, top, right, bottom)
    """
    try:
        # Extract values with defaults
        left = float(geometry.get("left", 0))
        top = float(geometry.get("top", 0))
        width = float(geometry.get("width", img.width))
        height = float(geometry.get("height", img.height))

        # Include translate if present
        left += float(geometry.get("translate_x", 0))
        top += float(geometry.get("translate_y", 0))

        # Ensure within image bounds
        left = max(0, min(left, img.width))
        top = max(0, min(top, img.height))
        right = max(0, min(left + width, img.width))
        bottom = max(0, min(top + height, img.height))

        return (int(left), int(top), int(right), int(bottom))
    except (ValueError, TypeError):
        # Return full image bounds on error
        return (0, 0, img.width, img.height)


def _is_valid_bbox(bbox: Tuple[int, int, int, int]) -> bool:
    """
    Check if bounding box has valid dimensions.
    
    Args:
        bbox: (left, top, right, bottom)
        
    Returns:
        True if bbox has area, False otherwise
    """
    try:
        left, top, right, bottom = bbox
        return right > left and bottom > top
    except (ValueError, TypeError):
        return False