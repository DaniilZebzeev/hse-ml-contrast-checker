"""
WCAG accessibility compliance checking module.

Implements WCAG 2.0/2.1 standards for color contrast accessibility.
"""

from enum import Enum
from typing import Tuple, Dict
import numpy as np
from .color_analysis import calculate_contrast_ratio


class WCAGLevel(Enum):
    """WCAG compliance levels."""
    AA = "AA"
    AAA = "AAA"


class TextSize(Enum):
    """Text size categories for WCAG compliance."""
    NORMAL = "normal"  # Less than 18pt (24px) or 14pt bold (18.66px bold)
    LARGE = "large"    # At least 18pt (24px) or 14pt bold (18.66px bold)


class WCAGChecker:
    """
    Checker for WCAG color contrast compliance.
    
    WCAG 2.0 Level AA requires:
    - 4.5:1 for normal text
    - 3:1 for large text
    
    WCAG 2.0 Level AAA requires:
    - 7:1 for normal text
    - 4.5:1 for large text
    """
    
    # Minimum contrast ratios for different text sizes and WCAG levels
    CONTRAST_REQUIREMENTS = {
        (TextSize.NORMAL, WCAGLevel.AA): 4.5,
        (TextSize.NORMAL, WCAGLevel.AAA): 7.0,
        (TextSize.LARGE, WCAGLevel.AA): 3.0,
        (TextSize.LARGE, WCAGLevel.AAA): 4.5,
    }
    
    def __init__(self):
        """Initialize the WCAG checker."""
        pass
    
    def check_contrast(self, 
                      text_color: Tuple[int, int, int], 
                      bg_color: Tuple[int, int, int],
                      text_size: TextSize = TextSize.NORMAL) -> Dict[str, any]:
        """
        Check if color contrast meets WCAG standards.
        
        Args:
            text_color: Text RGB color tuple (0-255)
            bg_color: Background RGB color tuple (0-255)
            text_size: Size of the text (normal or large)
            
        Returns:
            Dictionary with compliance results
        """
        contrast_ratio = calculate_contrast_ratio(text_color, bg_color)
        
        # Check compliance for each level
        aa_required = self.CONTRAST_REQUIREMENTS[(text_size, WCAGLevel.AA)]
        aaa_required = self.CONTRAST_REQUIREMENTS[(text_size, WCAGLevel.AAA)]
        
        aa_compliant = contrast_ratio >= aa_required
        aaa_compliant = contrast_ratio >= aaa_required
        
        result = {
            'contrast_ratio': contrast_ratio,
            'text_color': text_color,
            'background_color': bg_color,
            'text_size': text_size.value,
            'wcag_aa_compliant': aa_compliant,
            'wcag_aaa_compliant': aaa_compliant,
            'wcag_aa_required': aa_required,
            'wcag_aaa_required': aaa_required,
            'passes_wcag': aa_compliant,  # At minimum, should pass AA
        }
        
        return result
    
    def get_compliance_level(self,
                           text_color: Tuple[int, int, int],
                           bg_color: Tuple[int, int, int],
                           text_size: TextSize = TextSize.NORMAL) -> str:
        """
        Get the highest WCAG compliance level achieved.
        
        Args:
            text_color: Text RGB color tuple (0-255)
            bg_color: Background RGB color tuple (0-255)
            text_size: Size of the text (normal or large)
            
        Returns:
            String indicating compliance level: "AAA", "AA", or "Fail"
        """
        result = self.check_contrast(text_color, bg_color, text_size)
        
        if result['wcag_aaa_compliant']:
            return "AAA"
        elif result['wcag_aa_compliant']:
            return "AA"
        else:
            return "Fail"
    
    def suggest_improvements(self,
                           text_color: Tuple[int, int, int],
                           bg_color: Tuple[int, int, int],
                           text_size: TextSize = TextSize.NORMAL,
                           target_level: WCAGLevel = WCAGLevel.AA) -> Dict[str, any]:
        """
        Suggest color improvements to meet WCAG standards.
        
        Args:
            text_color: Text RGB color tuple (0-255)
            bg_color: Background RGB color tuple (0-255)
            text_size: Size of the text (normal or large)
            target_level: Target WCAG compliance level
            
        Returns:
            Dictionary with suggestions
        """
        current_result = self.check_contrast(text_color, bg_color, text_size)
        target_ratio = self.CONTRAST_REQUIREMENTS[(text_size, target_level)]
        
        suggestions = {
            'current_contrast': current_result['contrast_ratio'],
            'target_contrast': target_ratio,
            'needs_improvement': current_result['contrast_ratio'] < target_ratio,
        }
        
        if suggestions['needs_improvement']:
            improvement_factor = target_ratio / current_result['contrast_ratio']
            suggestions['suggestions'] = [
                f"Increase contrast ratio by a factor of {improvement_factor:.2f}",
                "Consider darkening the text color or lightening the background",
                "Consider using larger text if possible (reduces requirement to 3:1 for AA)",
            ]
        else:
            suggestions['suggestions'] = ["Colors already meet WCAG standards!"]
        
        return suggestions
    
    def batch_check(self, color_pairs: list, text_size: TextSize = TextSize.NORMAL) -> list:
        """
        Check multiple color pairs at once.
        
        Args:
            color_pairs: List of (text_color, bg_color) tuples
            text_size: Size of the text
            
        Returns:
            List of compliance results
        """
        results = []
        for text_color, bg_color in color_pairs:
            result = self.check_contrast(text_color, bg_color, text_size)
            results.append(result)
        
        return results
