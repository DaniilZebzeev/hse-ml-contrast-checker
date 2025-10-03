"""
Unit tests for the main contrast checker.
"""

import unittest
import numpy as np
import tempfile
import os
from PIL import Image
from contrast_checker.contrast_checker import ContrastChecker
from contrast_checker.accessibility import TextSize


class TestContrastChecker(unittest.TestCase):
    """Test cases for the main ContrastChecker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = ContrastChecker()
        
        # Create a temporary test image
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.test_image[:50, :, :] = [0, 0, 0]      # Black top half
        self.test_image[50:, :, :] = [255, 255, 255]  # White bottom half
        
        # Save to temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img = Image.fromarray(self.test_image)
        img.save(self.temp_file.name)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_check_image(self):
        """Test image checking."""
        result = self.checker.check_image(self.temp_file.name)
        
        # Check result structure
        self.assertIn('image_path', result)
        self.assertIn('text_color_rgb', result)
        self.assertIn('background_color_rgb', result)
        self.assertIn('contrast_ratio', result)
        self.assertIn('wcag_compliance', result)
        self.assertIn('text_size', result)
        
        # Check WCAG compliance structure
        self.assertIn('aa_compliant', result['wcag_compliance'])
        self.assertIn('aaa_compliant', result['wcag_compliance'])
        self.assertIn('level', result['wcag_compliance'])
    
    def test_check_colors_rgb(self):
        """Test checking specific RGB colors."""
        result = self.checker.check_colors(
            (0, 0, 0),
            (255, 255, 255),
            TextSize.NORMAL
        )
        
        # Should pass both AA and AAA
        self.assertTrue(result['wcag_compliance']['aa_compliant'])
        self.assertTrue(result['wcag_compliance']['aaa_compliant'])
        self.assertEqual(result['wcag_compliance']['level'], 'AAA')
        
        # Check hex conversion
        self.assertEqual(result['text_color_hex'], '#000000')
        self.assertEqual(result['background_color_hex'], '#ffffff')
    
    def test_check_colors_hex(self):
        """Test checking specific hex colors."""
        result = self.checker.check_colors(
            '#000000',
            '#FFFFFF',
            TextSize.NORMAL
        )
        
        # Should pass both AA and AAA
        self.assertTrue(result['wcag_compliance']['aa_compliant'])
        self.assertTrue(result['wcag_compliance']['aaa_compliant'])
        
        # Check RGB conversion
        self.assertEqual(result['text_color_rgb'], (0, 0, 0))
        self.assertEqual(result['background_color_rgb'], (255, 255, 255))
    
    def test_check_colors_failing(self):
        """Test checking colors that fail WCAG."""
        result = self.checker.check_colors(
            (200, 200, 200),
            (255, 255, 255),
            TextSize.NORMAL
        )
        
        # Should fail
        self.assertFalse(result['wcag_compliance']['aa_compliant'])
        self.assertEqual(result['wcag_compliance']['level'], 'Fail')
        
        # Should have suggestions
        self.assertIn('suggestions', result)
        self.assertTrue(result['suggestions']['needs_improvement'])
    
    def test_hex_to_rgb(self):
        """Test hex to RGB conversion."""
        rgb = self.checker._hex_to_rgb('#FF0000')
        self.assertEqual(rgb, (255, 0, 0))
        
        rgb = self.checker._hex_to_rgb('00FF00')
        self.assertEqual(rgb, (0, 255, 0))
    
    def test_rgb_to_hex(self):
        """Test RGB to hex conversion."""
        hex_color = self.checker._rgb_to_hex((255, 0, 0))
        self.assertEqual(hex_color, '#ff0000')
        
        hex_color = self.checker._rgb_to_hex((0, 255, 0))
        self.assertEqual(hex_color, '#00ff00')
    
    def test_generate_report(self):
        """Test report generation."""
        result = self.checker.check_colors(
            (0, 0, 0),
            (255, 255, 255),
            TextSize.NORMAL
        )
        
        report = self.checker.generate_report(result)
        
        # Report should be a string
        self.assertIsInstance(report, str)
        
        # Should contain key information
        self.assertIn('CONTRAST ANALYSIS REPORT', report)
        self.assertIn('Contrast Ratio:', report)
        self.assertIn('WCAG Compliance:', report)
        self.assertIn('Level AA:', report)
        self.assertIn('Level AAA:', report)
    
    def test_generate_report_with_image(self):
        """Test report generation with image path."""
        result = self.checker.check_image(self.temp_file.name)
        report = self.checker.generate_report(result)
        
        # Should include image path
        self.assertIn(self.temp_file.name, report)
    
    def test_generate_report_with_suggestions(self):
        """Test report generation with improvement suggestions."""
        result = self.checker.check_colors(
            (200, 200, 200),
            (255, 255, 255),
            TextSize.NORMAL
        )
        
        report = self.checker.generate_report(result)
        
        # Should include suggestions section
        self.assertIn('Suggestions for Improvement:', report)


if __name__ == '__main__':
    unittest.main()
