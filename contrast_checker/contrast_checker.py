"""
Main contrast checker module that integrates all components.
"""

import numpy as np
from typing import Dict, Tuple, Optional, Union
from .color_analysis import ColorAnalyzer, calculate_contrast_ratio
from .image_processing import ImageProcessor
from .accessibility import WCAGChecker, TextSize


class ContrastChecker:
    """
    Main class for comprehensive contrast checking with ML-based analysis.
    """
    
    def __init__(self):
        """Initialize the contrast checker with all components."""
        self.color_analyzer = ColorAnalyzer()
        self.image_processor = ImageProcessor()
        self.wcag_checker = WCAGChecker()
    
    def check_image(self, 
                   image_path: str,
                   text_size: TextSize = TextSize.NORMAL,
                   use_ml: bool = True) -> Dict[str, any]:
        """
        Analyze an image for text/background contrast compliance.
        
        Args:
            image_path: Path to the image file
            text_size: Size category of the text
            use_ml: Whether to use ML-based color extraction
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        # Load and preprocess image
        image = self.image_processor.load_image(image_path)
        image = self.image_processor.resize_image(image)
        image = self.image_processor.preprocess_image(image)
        
        # Extract text and background colors
        if use_ml:
            text_color, bg_color = self.color_analyzer.separate_text_background(image)
        else:
            text_color, bg_color = self.image_processor.get_text_background_colors(image)
        
        # Check WCAG compliance
        wcag_result = self.wcag_checker.check_contrast(
            tuple(text_color), 
            tuple(bg_color), 
            text_size
        )
        
        # Get color distribution statistics
        color_stats = self.color_analyzer.analyze_color_distribution(image)
        
        # Compile results
        result = {
            'image_path': image_path,
            'text_color_rgb': tuple(int(c) for c in text_color),
            'background_color_rgb': tuple(int(c) for c in bg_color),
            'contrast_ratio': wcag_result['contrast_ratio'],
            'wcag_compliance': {
                'aa_compliant': wcag_result['wcag_aa_compliant'],
                'aaa_compliant': wcag_result['wcag_aaa_compliant'],
                'level': self.wcag_checker.get_compliance_level(
                    tuple(text_color), 
                    tuple(bg_color), 
                    text_size
                ),
            },
            'text_size': text_size.value,
            'color_statistics': {
                'mean_color': tuple(int(c) for c in color_stats['mean_color']),
                'std_color': tuple(int(c) for c in color_stats['std_color']),
            },
        }
        
        return result
    
    def check_colors(self,
                    text_color: Union[Tuple[int, int, int], str],
                    bg_color: Union[Tuple[int, int, int], str],
                    text_size: TextSize = TextSize.NORMAL) -> Dict[str, any]:
        """
        Check contrast between two specific colors.
        
        Args:
            text_color: Text color as RGB tuple or hex string
            bg_color: Background color as RGB tuple or hex string
            text_size: Size category of the text
            
        Returns:
            Dictionary with analysis results
        """
        # Convert hex to RGB if needed
        if isinstance(text_color, str):
            text_color = self._hex_to_rgb(text_color)
        if isinstance(bg_color, str):
            bg_color = self._hex_to_rgb(bg_color)
        
        # Check WCAG compliance
        wcag_result = self.wcag_checker.check_contrast(text_color, bg_color, text_size)
        
        # Get suggestions if needed
        suggestions = self.wcag_checker.suggest_improvements(
            text_color, 
            bg_color, 
            text_size
        )
        
        result = {
            'text_color_rgb': text_color,
            'background_color_rgb': bg_color,
            'text_color_hex': self._rgb_to_hex(text_color),
            'background_color_hex': self._rgb_to_hex(bg_color),
            'contrast_ratio': wcag_result['contrast_ratio'],
            'wcag_compliance': {
                'aa_compliant': wcag_result['wcag_aa_compliant'],
                'aaa_compliant': wcag_result['wcag_aaa_compliant'],
                'level': self.wcag_checker.get_compliance_level(text_color, bg_color, text_size),
            },
            'text_size': text_size.value,
            'suggestions': suggestions,
        }
        
        return result
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color string."""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    def generate_report(self, result: Dict[str, any]) -> str:
        """
        Generate a human-readable report from analysis results.
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 60,
            "CONTRAST ANALYSIS REPORT",
            "=" * 60,
        ]
        
        if 'image_path' in result:
            report_lines.append(f"Image: {result['image_path']}")
        
        report_lines.extend([
            f"\nColors:",
            f"  Text:       RGB{result['text_color_rgb']}",
            f"  Background: RGB{result['background_color_rgb']}",
        ])
        
        if 'text_color_hex' in result:
            report_lines.extend([
                f"  Text (hex):       {result['text_color_hex']}",
                f"  Background (hex): {result['background_color_hex']}",
            ])
        
        report_lines.extend([
            f"\nContrast Ratio: {result['contrast_ratio']:.2f}:1",
            f"\nWCAG Compliance:",
            f"  Level AA:  {'✓ PASS' if result['wcag_compliance']['aa_compliant'] else '✗ FAIL'}",
            f"  Level AAA: {'✓ PASS' if result['wcag_compliance']['aaa_compliant'] else '✗ FAIL'}",
            f"  Overall Level: {result['wcag_compliance']['level']}",
            f"\nText Size: {result['text_size']}",
        ])
        
        if 'suggestions' in result and result['suggestions']['needs_improvement']:
            report_lines.extend([
                f"\nSuggestions for Improvement:",
            ])
            for suggestion in result['suggestions']['suggestions']:
                report_lines.append(f"  • {suggestion}")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
