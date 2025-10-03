"""
Color analysis module for contrast checking.

Implements WCAG color contrast calculation algorithms and related utilities.
"""

import numpy as np
from typing import Tuple, Union


def calculate_relative_luminance(rgb: Union[Tuple[int, int, int], np.ndarray]) -> float:
    """
    Calculate the relative luminance of a color according to WCAG 2.0 specification.
    
    Formula from: https://www.w3.org/TR/WCAG20/#relativeluminancedef
    
    Args:
        rgb: RGB color tuple or array with values in range [0, 255]
        
    Returns:
        Relative luminance value in range [0, 1]
    """
    if isinstance(rgb, tuple):
        rgb = np.array(rgb)
    
    # Normalize to [0, 1]
    rgb = rgb / 255.0
    
    # Apply gamma correction
    def gamma_correct(channel):
        if channel <= 0.03928:
            return channel / 12.92
        else:
            return ((channel + 0.055) / 1.055) ** 2.4
    
    r, g, b = [gamma_correct(c) for c in rgb]
    
    # Calculate luminance using WCAG formula
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    return luminance


def calculate_contrast_ratio(color1: Union[Tuple[int, int, int], np.ndarray], 
                             color2: Union[Tuple[int, int, int], np.ndarray]) -> float:
    """
    Calculate the contrast ratio between two colors according to WCAG 2.0.
    
    Formula from: https://www.w3.org/TR/WCAG20/#contrast-ratiodef
    
    Args:
        color1: First RGB color tuple or array with values in range [0, 255]
        color2: Second RGB color tuple or array with values in range [0, 255]
        
    Returns:
        Contrast ratio in range [1, 21]
    """
    lum1 = calculate_relative_luminance(color1)
    lum2 = calculate_relative_luminance(color2)
    
    # Ensure lum1 is the lighter color
    if lum1 < lum2:
        lum1, lum2 = lum2, lum1
    
    # Calculate contrast ratio
    contrast_ratio = (lum1 + 0.05) / (lum2 + 0.05)
    
    return contrast_ratio


class ColorAnalyzer:
    """
    Advanced color analysis with machine learning-based color clustering.
    """
    
    def __init__(self):
        """Initialize the color analyzer."""
        pass
    
    def extract_dominant_colors(self, image: np.ndarray, n_colors: int = 2) -> np.ndarray:
        """
        Extract dominant colors from an image using K-means clustering.
        
        Args:
            image: Input image as numpy array (H, W, 3) in RGB format
            n_colors: Number of dominant colors to extract
            
        Returns:
            Array of dominant colors (n_colors, 3) in RGB format
        """
        from sklearn.cluster import KMeans
        
        # Reshape image to list of pixels
        pixels = image.reshape(-1, 3)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get cluster centers (dominant colors)
        dominant_colors = kmeans.cluster_centers_.astype(int)
        
        return dominant_colors
    
    def separate_text_background(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Separate text and background colors using ML-based clustering.
        
        Args:
            image: Input image as numpy array (H, W, 3) in RGB format
            
        Returns:
            Tuple of (text_color, background_color) as RGB arrays
        """
        # Extract 2 dominant colors
        colors = self.extract_dominant_colors(image, n_colors=2)
        
        # Determine which is text and which is background
        # Typically, text is darker (lower luminance)
        lum1 = calculate_relative_luminance(colors[0])
        lum2 = calculate_relative_luminance(colors[1])
        
        if lum1 < lum2:
            text_color, bg_color = colors[0], colors[1]
        else:
            text_color, bg_color = colors[1], colors[0]
        
        return text_color, bg_color
    
    def analyze_color_distribution(self, image: np.ndarray, n_bins: int = 256) -> dict:
        """
        Analyze color distribution in an image.
        
        Args:
            image: Input image as numpy array (H, W, 3) in RGB format
            n_bins: Number of histogram bins
            
        Returns:
            Dictionary with color statistics
        """
        hist_r = np.histogram(image[:, :, 0], bins=n_bins, range=(0, 256))[0]
        hist_g = np.histogram(image[:, :, 1], bins=n_bins, range=(0, 256))[0]
        hist_b = np.histogram(image[:, :, 2], bins=n_bins, range=(0, 256))[0]
        
        return {
            'red_histogram': hist_r,
            'green_histogram': hist_g,
            'blue_histogram': hist_b,
            'mean_color': image.mean(axis=(0, 1)).astype(int),
            'std_color': image.std(axis=(0, 1)).astype(int),
        }
