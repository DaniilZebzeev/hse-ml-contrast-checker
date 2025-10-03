"""
Example: Create test images and analyze their contrast.

This example demonstrates how to create test images with different
contrast levels and analyze them using the contrast checker.
"""

from PIL import Image, ImageDraw, ImageFont
import os
from contrast_checker import ContrastChecker
from contrast_checker.accessibility import TextSize

def create_test_image(filename, text_color, bg_color, text="Sample Text"):
    """Create a simple test image with text."""
    # Create image with background
    img = Image.new('RGB', (400, 200), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a nice font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        except:
            font = ImageFont.load_default()
    
    # Draw text in the center
    draw.text((50, 75), text, fill=text_color, font=font)
    
    # Save image
    img.save(filename)
    print(f"Created: {filename}")

def main():
    # Create examples directory if it doesn't exist
    os.makedirs('/tmp/contrast_examples', exist_ok=True)
    
    # Test cases with different contrast levels
    test_cases = [
        ('excellent_contrast.png', (0, 0, 0), (255, 255, 255), "High Contrast"),
        ('good_contrast.png', (85, 85, 85), (255, 255, 255), "Good Contrast"),
        ('borderline_contrast.png', (119, 119, 119), (255, 255, 255), "Borderline"),
        ('poor_contrast.png', (200, 200, 200), (255, 255, 255), "Poor Contrast"),
        ('inverted.png', (255, 255, 255), (0, 0, 0), "White on Black"),
    ]
    
    print("=" * 70)
    print("CREATING AND ANALYZING TEST IMAGES")
    print("=" * 70)
    print()
    
    # Initialize checker
    checker = ContrastChecker()
    
    for filename, text_color, bg_color, description in test_cases:
        filepath = f'/tmp/contrast_examples/{filename}'
        
        # Create the test image
        create_test_image(filepath, text_color, bg_color, description)
        
        # Analyze the image
        print(f"\nAnalyzing: {description}")
        print("-" * 70)
        
        result = checker.check_image(filepath, text_size=TextSize.NORMAL, use_ml=True)
        
        print(f"Detected Text Color:       RGB{result['text_color_rgb']}")
        print(f"Detected Background Color: RGB{result['background_color_rgb']}")
        print(f"Contrast Ratio:            {result['contrast_ratio']:.2f}:1")
        print(f"WCAG Compliance Level:     {result['wcag_compliance']['level']}")
        print(f"  - AA:  {'✓ PASS' if result['wcag_compliance']['aa_compliant'] else '✗ FAIL'}")
        print(f"  - AAA: {'✓ PASS' if result['wcag_compliance']['aaa_compliant'] else '✗ FAIL'}")
        
        if 'color_statistics' in result:
            print(f"Mean Image Color:          RGB{result['color_statistics']['mean_color']}")
    
    print("\n" + "=" * 70)
    print(f"Test images saved to: /tmp/contrast_examples/")
    print("=" * 70)

if __name__ == "__main__":
    main()
