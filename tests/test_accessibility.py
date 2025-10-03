"""
Unit tests for accessibility module.
"""

import unittest
from contrast_checker.accessibility import WCAGChecker, WCAGLevel, TextSize


class TestWCAGChecker(unittest.TestCase):
    """Test cases for WCAG compliance checking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = WCAGChecker()
    
    def test_black_white_normal_text(self):
        """Test black text on white background (normal size)."""
        result = self.checker.check_contrast(
            (0, 0, 0),
            (255, 255, 255),
            TextSize.NORMAL
        )
        
        # Black on white should pass both AA and AAA
        self.assertTrue(result['wcag_aa_compliant'])
        self.assertTrue(result['wcag_aaa_compliant'])
        self.assertGreater(result['contrast_ratio'], 7.0)
    
    def test_black_white_large_text(self):
        """Test black text on white background (large size)."""
        result = self.checker.check_contrast(
            (0, 0, 0),
            (255, 255, 255),
            TextSize.LARGE
        )
        
        # Should pass both levels
        self.assertTrue(result['wcag_aa_compliant'])
        self.assertTrue(result['wcag_aaa_compliant'])
    
    def test_gray_on_white_normal(self):
        """Test gray text on white background."""
        # #666 (102,102,102) on white passes AA but not AAA for normal text
        result = self.checker.check_contrast(
            (102, 102, 102),
            (255, 255, 255),
            TextSize.NORMAL
        )
        
        # Should pass AA but not AAA for normal text
        self.assertTrue(result['wcag_aa_compliant'])
        self.assertFalse(result['wcag_aaa_compliant'])
    
    def test_low_contrast_fails(self):
        """Test that low contrast fails compliance."""
        # Light gray on white should fail
        result = self.checker.check_contrast(
            (200, 200, 200),
            (255, 255, 255),
            TextSize.NORMAL
        )
        
        # Should fail both levels
        self.assertFalse(result['wcag_aa_compliant'])
        self.assertFalse(result['wcag_aaa_compliant'])
    
    def test_get_compliance_level_aaa(self):
        """Test compliance level detection for AAA."""
        level = self.checker.get_compliance_level(
            (0, 0, 0),
            (255, 255, 255),
            TextSize.NORMAL
        )
        self.assertEqual(level, "AAA")
    
    def test_get_compliance_level_aa(self):
        """Test compliance level detection for AA."""
        level = self.checker.get_compliance_level(
            (102, 102, 102),
            (255, 255, 255),
            TextSize.NORMAL
        )
        self.assertEqual(level, "AA")
    
    def test_get_compliance_level_fail(self):
        """Test compliance level detection for fail."""
        level = self.checker.get_compliance_level(
            (200, 200, 200),
            (255, 255, 255),
            TextSize.NORMAL
        )
        self.assertEqual(level, "Fail")
    
    def test_large_text_easier_requirements(self):
        """Test that large text has easier requirements."""
        color1 = (150, 150, 150)
        color2 = (255, 255, 255)
        
        normal_result = self.checker.check_contrast(color1, color2, TextSize.NORMAL)
        large_result = self.checker.check_contrast(color1, color2, TextSize.LARGE)
        
        # Large text requirements are more lenient
        self.assertLess(large_result['wcag_aa_required'], normal_result['wcag_aa_required'])
        self.assertLess(large_result['wcag_aaa_required'], normal_result['wcag_aaa_required'])
    
    def test_suggest_improvements_passing(self):
        """Test suggestions when colors already pass."""
        suggestions = self.checker.suggest_improvements(
            (0, 0, 0),
            (255, 255, 255),
            TextSize.NORMAL,
            WCAGLevel.AA
        )
        
        self.assertFalse(suggestions['needs_improvement'])
        self.assertIn("already meet", suggestions['suggestions'][0].lower())
    
    def test_suggest_improvements_failing(self):
        """Test suggestions when colors fail."""
        suggestions = self.checker.suggest_improvements(
            (200, 200, 200),
            (255, 255, 255),
            TextSize.NORMAL,
            WCAGLevel.AA
        )
        
        self.assertTrue(suggestions['needs_improvement'])
        self.assertGreater(len(suggestions['suggestions']), 0)
    
    def test_batch_check(self):
        """Test batch checking of color pairs."""
        color_pairs = [
            ((0, 0, 0), (255, 255, 255)),
            ((200, 200, 200), (255, 255, 255)),
        ]
        
        results = self.checker.batch_check(color_pairs, TextSize.NORMAL)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]['wcag_aa_compliant'])
        self.assertFalse(results[1]['wcag_aa_compliant'])
    
    def test_contrast_requirements_constants(self):
        """Test that contrast requirements are correct."""
        self.assertEqual(
            self.checker.CONTRAST_REQUIREMENTS[(TextSize.NORMAL, WCAGLevel.AA)],
            4.5
        )
        self.assertEqual(
            self.checker.CONTRAST_REQUIREMENTS[(TextSize.NORMAL, WCAGLevel.AAA)],
            7.0
        )
        self.assertEqual(
            self.checker.CONTRAST_REQUIREMENTS[(TextSize.LARGE, WCAGLevel.AA)],
            3.0
        )
        self.assertEqual(
            self.checker.CONTRAST_REQUIREMENTS[(TextSize.LARGE, WCAGLevel.AAA)],
            4.5
        )


if __name__ == '__main__':
    unittest.main()
