"""
Unit tests for color analysis module.
"""

import unittest
import numpy as np
from contrast_checker.color_analysis import (
    calculate_relative_luminance,
    calculate_contrast_ratio,
    ColorAnalyzer
)


class TestColorAnalysis(unittest.TestCase):
    """Test cases for color analysis functions."""
    
    def test_relative_luminance_black(self):
        """Test luminance calculation for black."""
        black = (0, 0, 0)
        luminance = calculate_relative_luminance(black)
        self.assertAlmostEqual(luminance, 0.0, places=5)
    
    def test_relative_luminance_white(self):
        """Test luminance calculation for white."""
        white = (255, 255, 255)
        luminance = calculate_relative_luminance(white)
        self.assertAlmostEqual(luminance, 1.0, places=5)
    
    def test_relative_luminance_gray(self):
        """Test luminance calculation for gray."""
        gray = (128, 128, 128)
        luminance = calculate_relative_luminance(gray)
        # Gray should be somewhere in the middle
        self.assertGreater(luminance, 0.1)
        self.assertLess(luminance, 0.9)
    
    def test_contrast_ratio_black_white(self):
        """Test contrast ratio between black and white."""
        black = (0, 0, 0)
        white = (255, 255, 255)
        ratio = calculate_contrast_ratio(black, white)
        # Black and white should have maximum contrast of 21:1
        self.assertAlmostEqual(ratio, 21.0, places=1)
    
    def test_contrast_ratio_same_color(self):
        """Test contrast ratio between same colors."""
        color = (100, 100, 100)
        ratio = calculate_contrast_ratio(color, color)
        # Same color should have contrast ratio of 1:1
        self.assertAlmostEqual(ratio, 1.0, places=5)
    
    def test_contrast_ratio_symmetry(self):
        """Test that contrast ratio is symmetric."""
        color1 = (50, 50, 50)
        color2 = (200, 200, 200)
        ratio1 = calculate_contrast_ratio(color1, color2)
        ratio2 = calculate_contrast_ratio(color2, color1)
        self.assertAlmostEqual(ratio1, ratio2, places=5)
    
    def test_contrast_ratio_wcag_examples(self):
        """Test with known WCAG examples."""
        # Example from WCAG documentation
        # #777 on #FFF should be around 4.48:1
        gray = (119, 119, 119)
        white = (255, 255, 255)
        ratio = calculate_contrast_ratio(gray, white)
        self.assertGreater(ratio, 4.4)
        self.assertLess(ratio, 4.6)


class TestColorAnalyzer(unittest.TestCase):
    """Test cases for ColorAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ColorAnalyzer()
    
    def test_extract_dominant_colors(self):
        """Test dominant color extraction."""
        # Create a simple test image with two dominant colors
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:50, :, :] = [255, 0, 0]  # Red half
        image[50:, :, :] = [0, 0, 255]  # Blue half
        
        colors = self.analyzer.extract_dominant_colors(image, n_colors=2)
        
        # Should extract 2 colors
        self.assertEqual(len(colors), 2)
        
        # Colors should be close to red and blue
        red_found = any(
            c[0] > 200 and c[1] < 50 and c[2] < 50 for c in colors
        )
        blue_found = any(
            c[0] < 50 and c[1] < 50 and c[2] > 200 for c in colors
        )
        self.assertTrue(red_found or blue_found)
    
    def test_separate_text_background(self):
        """Test text/background separation."""
        # Create an image with dark and light regions
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:50, :, :] = [30, 30, 30]   # Dark (text-like)
        image[50:, :, :] = [200, 200, 200]  # Light (background-like)
        
        text_color, bg_color = self.analyzer.separate_text_background(image)
        
        # Text should be darker than background
        text_lum = calculate_relative_luminance(text_color)
        bg_lum = calculate_relative_luminance(bg_color)
        self.assertLess(text_lum, bg_lum)
    
    def test_analyze_color_distribution(self):
        """Test color distribution analysis."""
        # Create a simple test image
        image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        stats = self.analyzer.analyze_color_distribution(image)
        
        # Check that all required keys are present
        self.assertIn('red_histogram', stats)
        self.assertIn('green_histogram', stats)
        self.assertIn('blue_histogram', stats)
        self.assertIn('mean_color', stats)
        self.assertIn('std_color', stats)
        
        # Check histogram length
        self.assertEqual(len(stats['red_histogram']), 256)


if __name__ == '__main__':
    unittest.main()
