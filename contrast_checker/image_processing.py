"""
Image processing module for extracting text and background regions.

Uses computer vision and ML techniques for image analysis.
"""

import numpy as np
import cv2
from PIL import Image
from typing import Tuple, Optional, Union


class ImageProcessor:
    """
    Image processing utilities for contrast analysis.
    """
    
    def __init__(self):
        """Initialize the image processor."""
        pass
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from file path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image as numpy array in RGB format
        """
        img = Image.open(image_path)
        img = img.convert('RGB')
        return np.array(img)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better contrast analysis.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to float for processing
        img_float = image.astype(np.float32) / 255.0
        
        # Apply slight Gaussian blur to reduce noise
        img_blur = cv2.GaussianBlur(img_float, (3, 3), 0)
        
        # Convert back to uint8
        img_processed = (img_blur * 255).astype(np.uint8)
        
        return img_processed
    
    def detect_text_regions(self, image: np.ndarray) -> np.ndarray:
        """
        Detect text regions in the image using edge detection and morphological operations.
        
        Args:
            image: Input image as numpy array in RGB format
            
        Returns:
            Binary mask of text regions
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Apply morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return binary
    
    def extract_text_mask(self, image: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """
        Extract text regions using multiple techniques.
        
        Args:
            image: Input image as numpy array in RGB format
            threshold: Threshold for binary classification
            
        Returns:
            Binary mask where 1 indicates text regions
        """
        # Method 1: Edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Method 2: Variance-based (text usually has high local variance)
        kernel_size = 5
        gray_float = gray.astype(np.float32)
        mean = cv2.blur(gray_float, (kernel_size, kernel_size))
        sqr_mean = cv2.blur(gray_float ** 2, (kernel_size, kernel_size))
        variance = sqr_mean - mean ** 2
        variance_norm = (variance - variance.min()) / (variance.max() - variance.min() + 1e-6)
        
        # Combine methods
        text_mask = ((edges > 0) | (variance_norm > threshold)).astype(np.uint8)
        
        return text_mask
    
    def get_text_background_colors(self, image: np.ndarray, 
                                   text_mask: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract average text and background colors from image.
        
        Args:
            image: Input image as numpy array in RGB format
            text_mask: Optional binary mask indicating text regions
            
        Returns:
            Tuple of (text_color, background_color) as RGB arrays
        """
        if text_mask is None:
            text_mask = self.extract_text_mask(image)
        
        # Ensure text_mask is 2D
        if len(text_mask.shape) == 3:
            text_mask = text_mask[:, :, 0]
        
        # Calculate average colors
        text_pixels = image[text_mask > 0]
        bg_pixels = image[text_mask == 0]
        
        if len(text_pixels) == 0:
            # If no text detected, use darkest pixels as text
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            threshold_val = np.percentile(gray, 30)
            text_mask = (gray < threshold_val).astype(np.uint8)
            text_pixels = image[text_mask > 0]
        
        if len(bg_pixels) == 0:
            # If no background detected, use brightest pixels
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            threshold_val = np.percentile(gray, 70)
            bg_mask = (gray >= threshold_val).astype(np.uint8)
            bg_pixels = image[bg_mask > 0]
        
        text_color = text_pixels.mean(axis=0).astype(int) if len(text_pixels) > 0 else np.array([0, 0, 0])
        bg_color = bg_pixels.mean(axis=0).astype(int) if len(bg_pixels) > 0 else np.array([255, 255, 255])
        
        return text_color, bg_color
    
    def resize_image(self, image: np.ndarray, max_dimension: int = 800) -> np.ndarray:
        """
        Resize image to reduce processing time while maintaining aspect ratio.
        
        Args:
            image: Input image as numpy array
            max_dimension: Maximum dimension (width or height)
            
        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        
        if max(h, w) <= max_dimension:
            return image
        
        if h > w:
            new_h = max_dimension
            new_w = int(w * (max_dimension / h))
        else:
            new_w = max_dimension
            new_h = int(h * (max_dimension / w))
        
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized
