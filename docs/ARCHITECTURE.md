# 🏗️ System Architecture

## Overview

HSE ML Contrast Checker follows a **modular, layered architecture** designed for maintainability, testability, and extensibility.

## High-Level Architecture

```
┌───────────────────────────────────────────────────┐
│                  User Interface                    │
│              (CLI via click library)               │
└─────────────────────┬─────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────┐
│              Application Layer                     │
│           (contrast_checker.py)                    │
│    • Orchestrates analysis workflow                │
│    • Coordinates between modules                   │
│    • Handles JSON I/O                              │
└──┬────────────┬────────────┬────────────┬─────────┘
   │            │            │            │
┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐
│ Color   │ │  HTML   │ │ Image   │ │  WCAG   │
│ Parser  │ │ Parser  │ │Analyzer │ │Calculator│
└─────────┘ └─────────┘ └─────────┘ └─────────┘
   Domain Layer (Business Logic)
```

## Layer Breakdown

### 1. Presentation Layer

**Module**: `cli.py`

**Responsibilities**:
- Parse command-line arguments
- Validate input files
- Display progress and results
- Handle error formatting

**Technology**: `click` library

**Key Functions**:
- `main()`: Entry point for CLI

### 2. Application Layer

**Module**: `contrast_checker.py`

**Responsibilities**:
- Orchestrate analysis workflow
- Coordinate between domain modules
- Aggregate results
- Handle JSON serialization

**Key Functions**:
- `analyze_slide()`: Main analysis orchestrator
- `determine_effective_background()`: Background color resolution
- `analyze_entity_contrast()`: Per-entity analysis

### 3. Domain Layer

#### 3.1 Color Parser (`color_parser.py`)

**Purpose**: Parse and manipulate CSS colors

**Key Classes**:
- `RGBA`: Color representation with alpha

**Key Functions**:
- `parse_css_color()`: Parse hex/rgb/rgba/hsl/hsla
- `blend_over()`: Alpha compositing
- `hsl_to_rgb()`: Color space conversion
- `parse_font_size_px()`: Font size normalization

**Dependencies**: None (pure Python)

#### 3.2 HTML Parser (`html_parser.py`)

**Purpose**: Extract text entities from HTML

**Key Functions**:
- `extract_entities()`: Find all text entities
- `extract_font_info()`: Parse font properties
- `extract_geometry()`: Parse positioning

**Dependencies**: `BeautifulSoup4`, `lxml`

**Design Pattern**: Strategy (different parsers for different HTML structures)

#### 3.3 Image Analyzer (`image_analyzer.py`)

**Purpose**: ML-based dominant color extraction

**Key Functions**:
- `dominant_colors_mediancut()`: Median-cut algorithm
- `dominant_colors_kmeans()`: K-means clustering
- `analyze_image_region()`: Region-specific analysis

**Dependencies**: `Pillow`, `scikit-learn`, `numpy`

**Design Pattern**: Strategy (interchangeable ML algorithms)

#### 3.4 WCAG Calculator (`wcag.py`)

**Purpose**: WCAG 2.2 contrast calculations

**Key Functions**:
- `relative_luminance()`: Calculate color luminance
- `contrast_ratio()`: Calculate contrast ratio
- `classify_wcag()`: Determine WCAG level
- `suggest_fixes()`: Generate improvement suggestions

**Dependencies**: None (pure Python + math)

**Design Pattern**: Utility functions (stateless)

### 4. Reporting Layer

**Module**: `report_generator.py`

**Responsibilities**:
- Generate HTML reports
- Visualize color combinations
- Format WCAG badges
- Present suggestions

**Output**: Static HTML file

## Data Flow

```
1. User Input (JSON + optional image)
   ↓
2. CLI validates and parses arguments
   ↓
3. contrast_checker.analyze_slide()
   ├─→ Load JSON slide data
   ├─→ Load background image (if provided)
   ├─→ Determine effective background color
   │   ├─→ If base_color: parse_css_color()
   │   └─→ If image: dominant_colors_*(image, method)
   ├─→ Extract HTML entities
   │   └─→ html_parser.extract_entities(html)
   └─→ For each entity:
       ├─→ Extract font info
       ├─→ Extract text colors (weighted)
       ├─→ Calculate contrasts
       │   └─→ wcag.contrast_ratio(text, bg)
       ├─→ Classify WCAG levels
       │   └─→ wcag.classify_wcag(ratio, size, weight)
       └─→ Generate suggestions (if failed)
           └─→ wcag.suggest_fixes(...)
   ↓
4. Aggregate results
   ↓
5. Output JSON and HTML reports
```

## Module Dependencies

```
cli.py
  └─→ contrast_checker.py
      ├─→ color_parser.py
      ├─→ html_parser.py
      │   └─→ color_parser.py
      ├─→ image_analyzer.py
      └─→ wcag.py

report_generator.py
  (no internal dependencies)
```

**Dependency Rules**:
- ✅ Domain modules can depend on other domain modules
- ✅ Application layer can depend on domain layer
- ✅ Presentation layer can depend on application layer
- ❌ No circular dependencies
- ❌ Domain modules should NOT depend on application layer

## Design Patterns

### Strategy Pattern

Used for **ML algorithm selection**:

```python
if method == 'kmeans':
    colors = dominant_colors_kmeans(img, k=k)
else:
    colors = dominant_colors_mediancut(img, k=k)
```

**Benefits**:
- Easy to add new ML algorithms
- Runtime algorithm switching
- Testable in isolation

### Factory Pattern

Implicit in `parse_css_color()`:

```python
def parse_css_color(color: str) -> RGBA:
    if color.startswith('#'):
        # Hex parser
    elif 'rgb' in color:
        # RGB parser
    elif 'hsl' in color:
        # HSL parser
```

**Benefits**:
- Single entry point for all color formats
- Extensible to new formats

### Facade Pattern

`contrast_checker.analyze_slide()` acts as a **facade**:

```python
def analyze_slide(...):
    # Hides complexity of coordinating:
    # - Color parsing
    # - HTML parsing
    # - ML analysis
    # - WCAG calculation
```

**Benefits**:
- Simple API for complex operations
- Reduced coupling in CLI layer

## Testing Strategy

### Unit Tests

Each domain module has independent unit tests:

- `test_color_parser.py`: Pure functions, no dependencies
- `test_wcag.py`: Mathematical calculations
- `test_html_parser.py`: BeautifulSoup usage
- `test_image_analyzer.py`: ML algorithms (with fixtures)

**Coverage Target**: > 80%

### Integration Tests

Test interactions between modules:

- Color parsing → WCAG calculation
- HTML parsing → Font extraction
- Image analysis → Background determination

### End-to-End Tests

Full CLI invocations with example files:

```bash
python -m src.cli --slide-json examples/slide_color_bg.json
```

## Error Handling

### Error Propagation

```
CLI
 └─→ catch & format all errors
     └─→ Application Layer
         └─→ raise specific exceptions
             └─→ Domain Layer
                 └─→ raise ValueError/TypeError
```

### Error Types

- `FileNotFoundError`: Missing input files
- `ValueError`: Invalid JSON, malformed colors
- `TypeError`: Wrong parameter types

## Performance Considerations

### Bottlenecks

1. **Image loading**: Mitigated by resizing to 150x150
2. **K-means**: Slower than median-cut; user chooses
3. **HTML parsing**: BeautifulSoup is fast enough for slides

### Optimization Strategies

- **Lazy loading**: Load images only if needed
- **Caching**: Could cache dominant colors by image hash (future)
- **Parallel processing**: Could analyze entities in parallel (future)

## Extensibility Points

### Adding New Color Formats

Add to `parse_css_color()` in `color_parser.py`:

```python
if color.startswith('lab('):
    return parse_lab_color(color)
```

### Adding New ML Algorithms

Add new function in `image_analyzer.py`:

```python
def dominant_colors_gmm(img, k=5):
    # Gaussian Mixture Model implementation
    ...
```

Update CLI choices in `cli.py`.

### Adding New WCAG Versions

Update thresholds in `wcag.py`:

```python
def classify_wcag_3_0(ratio, font_size, font_weight):
    # WCAG 3.0 (APCA) calculations
    ...
```

## Deployment

### Docker Architecture

```
┌─────────────────────────┐
│  Stage 1: Builder       │
│  • Install dependencies │
│  • No source code       │
└───────────┬─────────────┘
            │
            │ Copy /root/.local
            ▼
┌─────────────────────────┐
│  Stage 2: Runtime       │
│  • Copy dependencies    │
│  • Copy source + examples│
│  • Lightweight image    │
└─────────────────────────┘
```

**Benefits**:
- Smaller final image
- No build tools in production
- Reproducible builds

### Directory Mounting

```yaml
volumes:
  - ./examples:/app/examples:ro  # Read-only
  - ./output:/app/output         # Read-write
```

## Future Architecture Improvements

1. **Plugin System**: Load custom ML algorithms dynamically
2. **REST API**: Wrap CLI in Flask/FastAPI
3. **Batch Processing**: Async analysis of multiple slides
4. **Database**: Store historical results
5. **Web UI**: React/Vue frontend

---

**Maintainer**: HSE ML Team
