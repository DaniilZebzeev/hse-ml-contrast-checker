"""
Command-line interface for the contrast checker tool.
"""

import argparse
import sys
import json
from .contrast_checker import ContrastChecker
from .accessibility import TextSize


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HSE ML Contrast Checker - Analyze text/background contrast for WCAG compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check an image file
  contrast-checker --image screenshot.png
  
  # Check specific colors (RGB)
  contrast-checker --text-color 0,0,0 --bg-color 255,255,255
  
  # Check specific colors (hex)
  contrast-checker --text-color "#000000" --bg-color "#FFFFFF"
  
  # Check with large text size
  contrast-checker --image screenshot.png --text-size large
  
  # Output as JSON
  contrast-checker --image screenshot.png --format json
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--image', '-i',
        type=str,
        help='Path to image file to analyze'
    )
    input_group.add_argument(
        '--colors', '-c',
        action='store_true',
        help='Check specific text and background colors'
    )
    
    # Color specification (for --colors mode)
    parser.add_argument(
        '--text-color', '-t',
        type=str,
        help='Text color as RGB tuple (e.g., "0,0,0") or hex (e.g., "#000000")'
    )
    parser.add_argument(
        '--bg-color', '-b',
        type=str,
        help='Background color as RGB tuple (e.g., "255,255,255") or hex (e.g., "#FFFFFF")'
    )
    
    # Analysis options
    parser.add_argument(
        '--text-size', '-s',
        type=str,
        choices=['normal', 'large'],
        default='normal',
        help='Text size category (default: normal)'
    )
    parser.add_argument(
        '--no-ml',
        action='store_true',
        help='Disable ML-based color extraction (use traditional methods)'
    )
    
    # Output options
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with detailed statistics'
    )
    
    args = parser.parse_args()
    
    # Validate color mode arguments
    if args.colors and (not args.text_color or not args.bg_color):
        parser.error("--colors mode requires both --text-color and --bg-color")
    
    # Initialize checker
    checker = ContrastChecker()
    
    # Convert text size to enum
    text_size = TextSize.LARGE if args.text_size == 'large' else TextSize.NORMAL
    
    try:
        # Perform analysis
        if args.image:
            result = checker.check_image(
                args.image,
                text_size=text_size,
                use_ml=not args.no_ml
            )
        else:
            # Parse colors
            text_color = parse_color(args.text_color)
            bg_color = parse_color(args.bg_color)
            
            result = checker.check_colors(
                text_color,
                bg_color,
                text_size=text_size
            )
        
        # Output results
        if args.format == 'json':
            # Convert numpy types to native Python types for JSON serialization
            result_json = convert_to_json_serializable(result)
            print(json.dumps(result_json, indent=2))
        else:
            report = checker.generate_report(result)
            print(report)
            
            if args.verbose and 'color_statistics' in result:
                print("\nDetailed Color Statistics:")
                print(f"  Mean Color: RGB{result['color_statistics']['mean_color']}")
                print(f"  Std Dev:    RGB{result['color_statistics']['std_color']}")
        
        # Exit with appropriate code
        if result['wcag_compliance']['aa_compliant']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"Error: Image file not found - {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


def parse_color(color_str: str):
    """Parse color string as RGB tuple or hex."""
    if color_str.startswith('#'):
        return color_str
    else:
        try:
            parts = color_str.split(',')
            return tuple(int(p.strip()) for p in parts)
        except ValueError:
            raise ValueError(f"Invalid color format: {color_str}. Use RGB tuple (e.g., '0,0,0') or hex (e.g., '#000000')")


def convert_to_json_serializable(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy array
        return obj.tolist()
    else:
        return obj


if __name__ == '__main__':
    main()
