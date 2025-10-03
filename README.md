# hse-ml-contrast-checker

Командный проект по анализу контрастности текста и фона с использованием ML методов. HSE Applied ML Course 2024/25

A Python-based tool for analyzing text and background contrast using machine learning approaches. Includes image processing, color analysis, and accessibility compliance checking (WCAG standards).

## Features

- ✅ **WCAG Compliance Checking**: Verify color contrast against WCAG 2.0/2.1 standards (AA and AAA levels)
- 🖼️ **Image Analysis**: Extract text and background colors from images using computer vision
- 🤖 **ML-Based Color Detection**: Use K-means clustering for dominant color extraction
- 🎨 **Color Analysis**: Calculate contrast ratios with precise WCAG algorithms
- 📊 **Multiple Input Methods**: Analyze images or specific color pairs (RGB/hex)
- 📝 **Detailed Reports**: Generate human-readable or JSON-formatted reports
- 💡 **Improvement Suggestions**: Get recommendations for better accessibility

## Installation

### From Source

```bash
git clone https://github.com/DaniilZebzeev/hse-ml-contrast-checker.git
cd hse-ml-contrast-checker
pip install -e .
```

### Requirements

- Python >= 3.8
- NumPy >= 1.24.0
- OpenCV >= 4.8.0
- Pillow >= 10.0.0
- scikit-learn >= 1.3.0
- scikit-image >= 0.21.0
- matplotlib >= 3.7.0
- scipy >= 1.11.0

## Usage

### Command Line Interface

The tool provides a command-line interface for easy usage:

#### Check Specific Colors

```bash
# Check black text on white background (RGB format)
contrast-checker --colors --text-color "0,0,0" --bg-color "255,255,255"

# Check colors using hex format
contrast-checker --colors --text-color "#000000" --bg-color "#FFFFFF"

# Check with large text size (relaxed requirements)
contrast-checker --colors --text-color "#666666" --bg-color "#FFFFFF" --text-size large
```

#### Analyze Images

```bash
# Analyze an image file
contrast-checker --image screenshot.png

# Use traditional image processing (without ML)
contrast-checker --image screenshot.png --no-ml

# Get verbose output with color statistics
contrast-checker --image screenshot.png --verbose
```

#### JSON Output

```bash
# Output results as JSON
contrast-checker --colors --text-color "#000000" --bg-color "#FFFFFF" --format json
```

### Python API

You can also use the tool programmatically in Python:

#### Check Specific Colors

```python
from contrast_checker import ContrastChecker
from contrast_checker.accessibility import TextSize

checker = ContrastChecker()

# Check colors (RGB tuples)
result = checker.check_colors(
    text_color=(0, 0, 0),
    bg_color=(255, 255, 255),
    text_size=TextSize.NORMAL
)

print(f"Contrast Ratio: {result['contrast_ratio']:.2f}:1")
print(f"WCAG AA: {'PASS' if result['wcag_compliance']['aa_compliant'] else 'FAIL'}")
print(f"WCAG AAA: {'PASS' if result['wcag_compliance']['aaa_compliant'] else 'FAIL'}")

# Check colors (hex strings)
result = checker.check_colors('#000000', '#FFFFFF')

# Generate a report
report = checker.generate_report(result)
print(report)
```

#### Analyze Images

```python
from contrast_checker import ContrastChecker
from contrast_checker.accessibility import TextSize

checker = ContrastChecker()

# Analyze an image
result = checker.check_image(
    'screenshot.png',
    text_size=TextSize.NORMAL,
    use_ml=True  # Use ML-based color extraction
)

print(f"Text Color: RGB{result['text_color_rgb']}")
print(f"Background Color: RGB{result['background_color_rgb']}")
print(f"Contrast Ratio: {result['contrast_ratio']:.2f}:1")
print(f"WCAG Level: {result['wcag_compliance']['level']}")

# Generate a report
report = checker.generate_report(result)
print(report)
```

#### Use Individual Components

```python
from contrast_checker.color_analysis import calculate_contrast_ratio, ColorAnalyzer
from contrast_checker.accessibility import WCAGChecker, WCAGLevel, TextSize
from contrast_checker.image_processing import ImageProcessor

# Calculate contrast ratio directly
ratio = calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
print(f"Contrast: {ratio:.2f}:1")

# Use color analyzer for ML-based color extraction
analyzer = ColorAnalyzer()
image = ImageProcessor().load_image('image.png')
text_color, bg_color = analyzer.separate_text_background(image)

# Check WCAG compliance
wcag = WCAGChecker()
result = wcag.check_contrast(text_color, bg_color, TextSize.NORMAL)
level = wcag.get_compliance_level(text_color, bg_color)
print(f"Compliance Level: {level}")

# Get improvement suggestions
suggestions = wcag.suggest_improvements(
    text_color, bg_color, 
    text_size=TextSize.NORMAL,
    target_level=WCAGLevel.AA
)
```

## WCAG Contrast Requirements

The tool checks against WCAG 2.0/2.1 standards:

| Text Size | WCAG AA | WCAG AAA |
|-----------|---------|----------|
| Normal text (<18pt or <14pt bold) | 4.5:1 | 7:1 |
| Large text (≥18pt or ≥14pt bold) | 3:1 | 4.5:1 |

## Examples

### Example Output (Text Format)

```
============================================================
CONTRAST ANALYSIS REPORT
============================================================

Colors:
  Text:       RGB(0, 0, 0)
  Background: RGB(255, 255, 255)
  Text (hex):       #000000
  Background (hex): #ffffff

Contrast Ratio: 21.00:1

WCAG Compliance:
  Level AA:  ✓ PASS
  Level AAA: ✓ PASS
  Overall Level: AAA

Text Size: normal
============================================================
```

### Example Output (JSON Format)

```json
{
  "text_color_rgb": [0, 0, 0],
  "background_color_rgb": [255, 255, 255],
  "text_color_hex": "#000000",
  "background_color_hex": "#ffffff",
  "contrast_ratio": 21.0,
  "wcag_compliance": {
    "aa_compliant": true,
    "aaa_compliant": true,
    "level": "AAA"
  },
  "text_size": "normal",
  "suggestions": {
    "current_contrast": 21.0,
    "target_contrast": 4.5,
    "needs_improvement": false,
    "suggestions": ["Colors already meet WCAG standards!"]
  }
}
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_color_analysis

# Run with verbose output
python -m unittest discover tests -v
```

## Project Structure

```
hse-ml-contrast-checker/
├── contrast_checker/
│   ├── __init__.py              # Package initialization
│   ├── accessibility.py         # WCAG compliance checking
│   ├── color_analysis.py        # Color analysis and ML algorithms
│   ├── contrast_checker.py      # Main contrast checker class
│   ├── image_processing.py      # Image processing utilities
│   └── cli.py                   # Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_accessibility.py
│   ├── test_color_analysis.py
│   ├── test_contrast_checker.py
│   └── test_image_processing.py
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── README.md                    # This file
└── LICENSE                      # MIT License
```

## Technical Details

### Color Analysis

- **Relative Luminance**: Calculated according to WCAG 2.0 specification with gamma correction
- **Contrast Ratio**: Computed as (L1 + 0.05) / (L2 + 0.05) where L1 is lighter color
- **ML-Based Extraction**: K-means clustering (sklearn) for dominant color detection

### Image Processing

- **Text Detection**: Edge detection, adaptive thresholding, and variance analysis
- **Color Extraction**: Combines traditional CV and ML approaches
- **Preprocessing**: Gaussian blur, noise reduction, and image resizing for efficiency

### Accessibility Standards

Fully compliant with:
- WCAG 2.0 Level AA and AAA
- WCAG 2.1 Level AA and AAA
- Section 508 accessibility guidelines

## Contributing

This is a course project for HSE Applied ML Course 2024/25. Contributions, bug reports, and feature requests are welcome!

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Authors

- Zebzeev Daniil - [@DaniilZebzeev](https://github.com/DaniilZebzeev)

## Acknowledgments

- HSE Applied ML Course 2024/25
- WCAG 2.0/2.1 Accessibility Guidelines
- Open source ML and CV libraries (scikit-learn, OpenCV, etc.)

