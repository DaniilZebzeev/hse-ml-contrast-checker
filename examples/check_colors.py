"""
Example: Check specific colors for WCAG compliance.

This example demonstrates how to check specific text and background colors
against WCAG accessibility standards.
"""

from contrast_checker import ContrastChecker
from contrast_checker.accessibility import TextSize

def main():
    # Initialize the checker
    checker = ContrastChecker()
    
    # Test cases: (text_color, bg_color, description)
    test_cases = [
        ((0, 0, 0), (255, 255, 255), "Black on White"),
        ((255, 255, 255), (0, 0, 0), "White on Black"),
        ((102, 102, 102), (255, 255, 255), "Gray on White (AA pass)"),
        ((119, 119, 119), (255, 255, 255), "Light Gray on White (borderline)"),
        ((204, 204, 204), (255, 255, 255), "Very Light Gray on White (fail)"),
        ("#0066CC", "#FFFFFF", "Blue on White"),
        ("#FF0000", "#000000", "Red on Black"),
    ]
    
    print("=" * 70)
    print("WCAG COLOR CONTRAST COMPLIANCE CHECKER")
    print("=" * 70)
    print()
    
    for text_color, bg_color, description in test_cases:
        print(f"\n{description}:")
        print("-" * 70)
        
        result = checker.check_colors(
            text_color=text_color,
            bg_color=bg_color,
            text_size=TextSize.NORMAL
        )
        
        print(f"Text:       {result['text_color_hex']} - RGB{result['text_color_rgb']}")
        print(f"Background: {result['background_color_hex']} - RGB{result['background_color_rgb']}")
        print(f"Contrast:   {result['contrast_ratio']:.2f}:1")
        print(f"WCAG AA:    {'✓ PASS' if result['wcag_compliance']['aa_compliant'] else '✗ FAIL'}")
        print(f"WCAG AAA:   {'✓ PASS' if result['wcag_compliance']['aaa_compliant'] else '✗ FAIL'}")
        
        if result['suggestions']['needs_improvement']:
            print("\nSuggestions:")
            for suggestion in result['suggestions']['suggestions']:
                print(f"  • {suggestion}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
