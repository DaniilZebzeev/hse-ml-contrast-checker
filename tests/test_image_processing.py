"""
Unit tests for image processing module.
"""

import unittest
import numpy as np
import tempfile
import os
from PIL import Image
from contrast_checker.image_processing import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    """Test cases for image processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor()
        
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
    
    def test_load_image(self):
        """Test image loading."""
        image = self.processor.load_image(self.temp_file.name)
        
        self.assertIsInstance(image, np.ndarray)
        self.assertEqual(len(image.shape), 3)
        self.assertEqual(image.shape[2], 3)  # RGB
    
    def test_preprocess_image(self):
        """Test image preprocessing."""
        processed = self.processor.preprocess_image(self.test_image)
        
        # Should return same shape
        self.assertEqual(processed.shape, self.test_image.shape)
        
        # Should be uint8
        self.assertEqual(processed.dtype, np.uint8)
    
    def test_detect_text_regions(self):
        """Test text region detection."""
        # Create an image with text-like patterns
        image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        # Add some dark strokes (simulating text)
        image[40:60, 20:25, :] = 0
        image[40:60, 30:35, :] = 0
        
        mask = self.processor.detect_text_regions(image)
        
        # Should return binary mask
        self.assertEqual(mask.dtype, np.uint8)
        self.assertEqual(len(mask.shape), 2)
        
        # Mask should have some detected regions
        self.assertGreater(mask.sum(), 0)
    
    def test_extract_text_mask(self):
        """Test text mask extraction."""
        mask = self.processor.extract_text_mask(self.test_image)
        
        # Should return binary mask
        self.assertIsInstance(mask, np.ndarray)
        self.assertEqual(len(mask.shape), 2)
    
    def test_get_text_background_colors(self):
        """Test text and background color extraction."""
        # Create an image with more distinct regions
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        test_img[:30, :, :] = [30, 30, 30]   # Dark region (text-like)
        test_img[30:, :, :] = [220, 220, 220]  # Light region (background-like)
        
        text_color, bg_color = self.processor.get_text_background_colors(test_img)
        
        # Should return RGB tuples
        self.assertEqual(len(text_color), 3)
        self.assertEqual(len(bg_color), 3)
        
        # Colors should be different
        # Check that they are reasonably different (not both gray)
        from contrast_checker.color_analysis import calculate_relative_luminance
        text_lum = calculate_relative_luminance(text_color)
        bg_lum = calculate_relative_luminance(bg_color)
        
        # They should have different luminance
        self.assertNotAlmostEqual(text_lum, bg_lum, places=1)
    
    def test_resize_image_no_resize_needed(self):
        """Test that small images are not resized."""
        small_image = np.zeros((100, 100, 3), dtype=np.uint8)
        resized = self.processor.resize_image(small_image, max_dimension=800)
        
        # Should be unchanged
        self.assertEqual(resized.shape, small_image.shape)
    
    def test_resize_image_large(self):
        """Test resizing large images."""
        large_image = np.zeros((1000, 1000, 3), dtype=np.uint8)
        resized = self.processor.resize_image(large_image, max_dimension=500)
        
        # Should be resized
        self.assertLessEqual(max(resized.shape[:2]), 500)
        
        # Aspect ratio should be maintained
        original_aspect = large_image.shape[0] / large_image.shape[1]
        resized_aspect = resized.shape[0] / resized.shape[1]
        self.assertAlmostEqual(original_aspect, resized_aspect, places=1)
    
    def test_resize_image_wide(self):
        """Test resizing wide images."""
        wide_image = np.zeros((100, 1000, 3), dtype=np.uint8)
        resized = self.processor.resize_image(wide_image, max_dimension=500)
        
        # Width should be limited to max_dimension
        self.assertLessEqual(resized.shape[1], 500)
    
    def test_resize_image_tall(self):
        """Test resizing tall images."""
        tall_image = np.zeros((1000, 100, 3), dtype=np.uint8)
        resized = self.processor.resize_image(tall_image, max_dimension=500)
        
        # Height should be limited to max_dimension
        self.assertLessEqual(resized.shape[0], 500)


if __name__ == '__main__':
    unittest.main()
