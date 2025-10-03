"""
Example: Using individual components of the contrast checker.

This example demonstrates how to use the individual modules
(color analysis, image processing, accessibility checking) separately.
"""

import numpy as np
from contrast_checker.color_analysis import (
    calculate_relative_luminance,
    calculate_contrast_ratio,
    ColorAnalyzer
)
from contrast_checker.accessibility import WCAGChecker, WCAGLevel, TextSize
from contrast_checker.image_processing import ImageProcessor

def example_color_analysis():
    """Demonstrate color analysis functions."""
    print("\n" + "=" * 70)
    print("COLOR ANALYSIS EXAMPLES")
    print("=" * 70)
    
    # Calculate relative luminance
    black = (0, 0, 0)
    white = (255, 255, 255)
    gray = (128, 128, 128)
    
    print(f"\nRelative Luminance:")
    print(f"  Black {black}: {calculate_relative_luminance(black):.4f}")
    print(f"  White {white}: {calculate_relative_luminance(white):.4f}")
    print(f"  Gray {gray}:  {calculate_relative_luminance(gray):.4f}")
    
    # Calculate contrast ratios
    print(f"\nContrast Ratios:")
    print(f"  Black on White: {calculate_contrast_ratio(black, white):.2f}:1")
    print(f"  Gray on White:  {calculate_contrast_ratio(gray, white):.2f}:1")
    print(f"  Gray on Black:  {calculate_contrast_ratio(gray, black):.2f}:1")

def example_ml_color_extraction():
    """Demonstrate ML-based color extraction."""
    print("\n" + "=" * 70)
    print("ML-BASED COLOR EXTRACTION")
    print("=" * 70)
    
    # Create a synthetic image with two dominant colors
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:50, :, :] = [50, 50, 50]   # Dark gray
    image[50:, :, :] = [200, 200, 200]  # Light gray
    
    # Add some noise
    noise = np.random.randint(-10, 10, image.shape, dtype=np.int16)
    image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    analyzer = ColorAnalyzer()
    
    # Extract dominant colors
    print(f"\nExtracting dominant colors from synthetic image...")
    dominant_colors = analyzer.extract_dominant_colors(image, n_colors=2)
    print(f"Dominant colors found:")
    for i, color in enumerate(dominant_colors, 1):
        print(f"  Color {i}: RGB{tuple(color)}")
    
    # Separate text and background
    text_color, bg_color = analyzer.separate_text_background(image)
    print(f"\nSeparated colors:")
    print(f"  Text (darker):  RGB{tuple(text_color)}")
    print(f"  Background:     RGB{tuple(bg_color)}")
    
    # Calculate their contrast
    contrast = calculate_contrast_ratio(text_color, bg_color)
    print(f"  Contrast ratio: {contrast:.2f}:1")

def example_wcag_checking():
    """Demonstrate WCAG compliance checking."""
    print("\n" + "=" * 70)
    print("WCAG COMPLIANCE CHECKING")
    print("=" * 70)
    
    checker = WCAGChecker()
    
    # Test different color combinations
    test_colors = [
        ((0, 0, 0), (255, 255, 255), "Black on White"),
        ((85, 85, 85), (255, 255, 255), "Dark Gray on White"),
        ((180, 180, 180), (255, 255, 255), "Light Gray on White"),
    ]
    
    print(f"\nChecking Normal Text Size:")
    print(f"  AA requirement:  4.5:1")
    print(f"  AAA requirement: 7.0:1\n")
    
    for text_color, bg_color, description in test_colors:
        result = checker.check_contrast(text_color, bg_color, TextSize.NORMAL)
        print(f"{description}:")
        print(f"  Contrast: {result['contrast_ratio']:.2f}:1")
        print(f"  AA:  {'✓' if result['wcag_aa_compliant'] else '✗'}")
        print(f"  AAA: {'✓' if result['wcag_aaa_compliant'] else '✗'}")
    
    # Show how large text has easier requirements
    print(f"\n\nChecking Large Text Size:")
    print(f"  AA requirement:  3.0:1")
    print(f"  AAA requirement: 4.5:1\n")
    
    text_color = (150, 150, 150)
    bg_color = (255, 255, 255)
    
    normal_result = checker.check_contrast(text_color, bg_color, TextSize.NORMAL)
    large_result = checker.check_contrast(text_color, bg_color, TextSize.LARGE)
    
    print(f"Medium Gray on White ({text_color} on {bg_color}):")
    print(f"  Contrast: {normal_result['contrast_ratio']:.2f}:1")
    print(f"  Normal text - AA: {'✓' if normal_result['wcag_aa_compliant'] else '✗'}")
    print(f"  Large text  - AA: {'✓' if large_result['wcag_aa_compliant'] else '✗'}")

def example_image_processing():
    """Demonstrate image processing capabilities."""
    print("\n" + "=" * 70)
    print("IMAGE PROCESSING")
    print("=" * 70)
    
    processor = ImageProcessor()
    
    # Create a test image
    print(f"\nCreating synthetic test image...")
    image = np.ones((200, 200, 3), dtype=np.uint8) * 255
    # Add some "text-like" dark strokes
    image[80:120, 50:55, :] = 30
    image[80:120, 65:70, :] = 30
    image[80:85, 50:70, :] = 30
    
    # Preprocess
    processed = processor.preprocess_image(image)
    print(f"Image preprocessed: shape {processed.shape}, dtype {processed.dtype}")
    
    # Detect text regions
    text_mask = processor.extract_text_mask(image)
    print(f"Text mask extracted: {text_mask.sum()} pixels detected as text")
    
    # Extract colors
    text_color, bg_color = processor.get_text_background_colors(image, text_mask)
    print(f"\nExtracted colors:")
    print(f"  Text:       RGB{tuple(text_color)}")
    print(f"  Background: RGB{tuple(bg_color)}")
    print(f"  Contrast:   {calculate_contrast_ratio(text_color, bg_color):.2f}:1")
    
    # Test resizing
    large_image = np.zeros((2000, 1500, 3), dtype=np.uint8)
    resized = processor.resize_image(large_image, max_dimension=800)
    print(f"\nImage resizing:")
    print(f"  Original: {large_image.shape}")
    print(f"  Resized:  {resized.shape}")

def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("CONTRAST CHECKER - COMPONENT EXAMPLES")
    print("=" * 70)
    
    example_color_analysis()
    example_ml_color_extraction()
    example_wcag_checking()
    example_image_processing()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
