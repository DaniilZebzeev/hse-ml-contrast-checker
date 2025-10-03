"""
HSE ML Contrast Checker

A Python-based tool for analyzing text and background contrast using machine learning approaches.
Includes image processing, color analysis, and accessibility compliance checking (WCAG standards).
"""

__version__ = "0.1.0"
__author__ = "Zebzeev Daniil"

from .color_analysis import ColorAnalyzer, calculate_contrast_ratio, calculate_relative_luminance
from .image_processing import ImageProcessor
from .accessibility import WCAGChecker, WCAGLevel
from .contrast_checker import ContrastChecker

__all__ = [
    "ColorAnalyzer",
    "calculate_contrast_ratio",
    "calculate_relative_luminance",
    "ImageProcessor",
    "WCAGChecker",
    "WCAGLevel",
    "ContrastChecker",
]
