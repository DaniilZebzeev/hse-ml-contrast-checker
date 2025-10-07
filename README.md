# 🎨 HSE ML Contrast Checker

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Production-ready Python tool for analyzing text-background contrast according to **WCAG 2.2** accessibility standards using **Machine Learning** algorithms.

## 📋 Overview

This tool analyzes contrast between text and background colors in presentation slides, using ML algorithms to extract dominant colors from backgrounds and calculate WCAG compliance. Perfect for ensuring your slides are accessible!

### ✨ Key Features

- ✅ **WCAG 2.2 Compliant**: Accurate contrast ratio calculation per WCAG standards
- 🤖 **ML-Powered**: Two unsupervised learning algorithms for color extraction:
  - **Median-cut** (faster, Pillow ADAPTIVE)
  - **K-means clustering** (more accurate, scikit-learn)
- 📊 **HTML Reports**: Beautiful visual reports with suggestions
- 🐳 **Docker Ready**: Multi-stage Docker build included
- 🧪 **Well Tested**: Comprehensive test suite with pytest
- 📝 **Type Safe**: Full type hints and mypy checked
- 🎯 **CLI Interface**: Easy-to-use command-line tool

## 🚀 Quick Start

### Installation

#### Option 1: Local Installation (venv)

```bash
# Clone repository
git clone https://github.com/DaniilZebzeev/hse-ml-contrast-checker.git
cd hse-ml-contrast-checker

# Create virtual environment
python -m venv venv

# Activate venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Docker

```bash
# Build image
docker build -t hse-contrast-checker .

# Or use docker-compose
docker-compose build
```

### Basic Usage

```bash
# Analyze slide with color background
python -m src.cli --slide-json examples/slide_color_bg.json

# Analyze with image background using K-means
python -m src.cli \
    --slide-json examples/slide_with_image.json \
    --bg-image examples/background.png \
    --ml-method kmeans

# Custom output paths
python -m src.cli \
    --slide-json examples/slide_complex.json \
    --out-json results/my_result.json \
    --out-html results/my_report.html \
    --verbose
```

### Docker Usage

```bash
# Using docker run
docker run -v $(pwd)/examples:/app/examples -v $(pwd)/output:/app/output \
    hse-contrast-checker --slide-json /app/examples/slide_color_bg.json

# Using docker-compose
docker-compose run contrast-checker \
    --slide-json /app/examples/slide_with_image.json \
    --bg-image /app/examples/background.png
```

## 📚 How It Works

### 1. Input Format

The tool accepts JSON files describing slides:

```json
{
  "id": "slide-001",
  "base_color": "#ffffff",
  "content_html": "<div id=\"text-1\">...</div>"
}
```

### 2. ML Color Extraction

**Median-cut Algorithm** (Default):
- Fast palette quantization
- Recursively divides color space
- O(n log n) complexity

**K-means Clustering**:
- More accurate for complex images
- Unsupervised learning approach
- Finds k cluster centers in RGB space

### 3. WCAG 2.2 Contrast Calculation

Formula: `(L1 + 0.05) / (L2 + 0.05)`

| Level | Normal Text | Large Text |
|-------|-------------|------------|
| AA    | 4.5:1       | 3:1        |
| AAA   | 7:1         | 4.5:1      |

**Large text** = 18pt+ (24px+) OR 14pt+ bold (18.67px+ bold)

### 4. Output

- **JSON**: Machine-readable analysis results
- **HTML**: Visual report with color previews and suggestions

## 🏗️ Architecture

```
┌─────────────────┐
│   CLI (click)   │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │ contrast_checker.py  │ ◄─── Main orchestrator
    └────┬─────────────────┘
         │
    ┌────▼──────────┬──────────────┬───────────────┐
    │               │              │               │
┌───▼────┐  ┌──────▼─────┐  ┌────▼─────┐  ┌─────▼────┐
│color_  │  │html_       │  │image_    │  │wcag.py   │
│parser  │  │parser      │  │analyzer  │  │          │
│        │  │(BS4)       │  │(ML)      │  │(formulas)│
└────────┘  └────────────┘  └──────────┘  └──────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Type checking
mypy src

# Linting
flake8 src tests
black --check src tests
```

## 📖 API Documentation

See [docs/API.md](docs/API.md) for detailed API reference.

## 🤖 ML Approach

This project uses **unsupervised learning** for color extraction:

### Median-cut Algorithm
- **Type**: Recursive palette quantization
- **Complexity**: O(n log k)
- **Pros**: Fast, deterministic
- **Cons**: Less accurate for complex gradients

### K-means Clustering
- **Type**: Iterative cluster optimization
- **Complexity**: O(n * k * i) where i = iterations
- **Pros**: More accurate, finds "true" dominant colors
- **Cons**: Slower, requires more memory

See [docs/ML_APPROACH.md](docs/ML_APPROACH.md) for mathematical details.

## 🔧 Configuration

### CLI Options

```
--slide-json PATH       Input slide JSON (required)
--slide-index INT       Slide index if JSON is array
--bg-image PATH         Background image file
--ml-method CHOICE      mediancut|kmeans (default: mediancut)
--k-colors INT          Number of colors to extract (default: 5)
--out-json PATH         Output JSON path
--out-html PATH         Output HTML report path
--verbose               Enable verbose logging
```

## 📊 Example Output

### Console Output
```
✓ Analysis complete!
  📊 Slide ID: slide-001
  📝 Total entities: 3
  ✅ Passed AA Normal: 2
  ❌ Failed AA Normal: 1

  📁 JSON: output/result.json
  🌐 HTML: output/report.html
```

### HTML Report
The HTML report includes:
- Summary with effective background color
- Per-entity contrast ratios
- WCAG compliance badges (AA Normal, AA Large, AAA)
- Visual previews of text/background combinations
- Actionable suggestions for failed entities

## 🛠️ Development

### Project Structure

```
hse-ml-contrast-checker/
├── src/
│   ├── color_parser.py       # CSS color parsing
│   ├── html_parser.py         # BeautifulSoup entity extraction
│   ├── image_analyzer.py      # ML algorithms
│   ├── wcag.py                # WCAG calculations
│   ├── contrast_checker.py    # Main orchestrator
│   ├── report_generator.py    # HTML report generator
│   └── cli.py                 # CLI interface
├── tests/                     # pytest tests
├── examples/                  # Example JSON files
├── docs/                      # Documentation
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Docker Compose config
└── requirements.txt           # Production dependencies
```

### Code Style

- **Formatting**: Black (line length 120)
- **Linting**: flake8
- **Type checking**: mypy
- **Docstrings**: Google style

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **HSE ML Team** - *Initial work*

## 🙏 Acknowledgments

- WCAG 2.2 Guidelines
- scikit-learn for K-means implementation
- Pillow for image processing
- BeautifulSoup for HTML parsing

## 📞 Support

For issues and questions, please use [GitHub Issues](https://github.com/DaniilZebzeev/hse-ml-contrast-checker/issues).

---

**Made with ❤️ for HSE Applied Machine Learning Course**
