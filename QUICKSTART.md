# Quick Start Guide

This guide will help you get started with the HSE ML Contrast Checker in just a few minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/DaniilZebzeev/hse-ml-contrast-checker.git
cd hse-ml-contrast-checker

# Install in development mode
pip install -e .
```

## Basic Usage

### 1. Check Two Colors

The simplest way to use the tool is to check two specific colors:

```bash
# Check black text on white background
contrast-checker --colors --text-color "#000000" --bg-color "#FFFFFF"
```

Output:
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

### 2. Check an Image

You can also analyze contrast in an image:

```bash
# Analyze a screenshot
contrast-checker --image screenshot.png
```

### 3. Use in Python

```python
from contrast_checker import ContrastChecker

# Create a checker instance
checker = ContrastChecker()

# Check colors
result = checker.check_colors('#000000', '#FFFFFF')

# Print results
print(f"Contrast Ratio: {result['contrast_ratio']:.2f}:1")
print(f"WCAG Level: {result['wcag_compliance']['level']}")
```

## Common Use Cases

### Check if colors meet WCAG AA

```bash
contrast-checker --colors \
  --text-color "#333333" \
  --bg-color "#FFFFFF"
```

### Check for large text (relaxed requirements)

```bash
contrast-checker --colors \
  --text-color "#666666" \
  --bg-color "#FFFFFF" \
  --text-size large
```

### Get JSON output for integration

```bash
contrast-checker --colors \
  --text-color "#000000" \
  --bg-color "#FFFFFF" \
  --format json
```

### Analyze image with verbose output

```bash
contrast-checker --image screenshot.png --verbose
```

## Understanding the Results

### Contrast Ratio
- The contrast ratio ranges from 1:1 (same color) to 21:1 (black and white)
- Higher ratios mean better readability

### WCAG Levels
- **AAA**: Highest level - 7:1 for normal text, 4.5:1 for large text
- **AA**: Standard level - 4.5:1 for normal text, 3:1 for large text
- **Fail**: Does not meet minimum standards

### Text Sizes
- **Normal**: Less than 18pt (24px) or 14pt bold (18.66px bold)
- **Large**: At least 18pt (24px) or 14pt bold (18.66px bold)

## Examples

Try the included examples:

```bash
# Check various color combinations
python examples/check_colors.py

# Create and analyze test images
python examples/analyze_images.py

# See how to use individual components
python examples/component_usage.py
```

## Running Tests

```bash
# Run all tests
python -m unittest discover tests -v
```

## Getting Help

```bash
# Show help and all options
contrast-checker --help
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [examples](examples/) directory
- Check the API documentation in the source code

## Troubleshooting

### "Module not found" error
Make sure you installed the package:
```bash
pip install -e .
```

### Image file not found
Use absolute paths or ensure the image file exists:
```bash
contrast-checker --image /full/path/to/image.png
```

### No module named 'cv2'
OpenCV might not be installed properly:
```bash
pip install opencv-python
```
