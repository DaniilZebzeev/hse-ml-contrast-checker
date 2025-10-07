# 🚀 МЕГА-ПРОМПТ ДЛЯ CLAUDE CODE CLI

Скопируйте этот промпт целиком и используйте в Claude Code CLI:

---

```
# ЗАДАЧА: Создать production-ready Python проект для анализа контрастности текста и фона (WCAG 2.2)

## КОНТЕКСТ ПРОЕКТА
Это учебный проект по курсу "Прикладные аспекты машинного обучения" (HSE). 
Требуется создать инструмент, который:
1. Принимает JSON с настройками слайда (base_color, custom_theme, HTML content)
2. Извлекает все текстовые entity с их цветами
3. Определяет доминирующие цвета фона (используя ML: median-cut или K-means)
4. Вычисляет контрастность текст/фон по стандарту WCAG 2.2
5. Возвращает JSON с оценкой контрастности для каждого entity

## КРИТИЧЕСКИЕ ТРЕБОВАНИЯ

### 1. СТРУКТУРА ПРОЕКТА
Создай следующую структуру:

```
hse-ml-contrast-checker/
├── .git/                          # Git репозиторий
├── .gitignore                     # Python + Docker + IDE
├── README.md                      # Подробная документация
├── LICENSE                        # MIT License
├── requirements.txt               # Зависимости production
├── requirements-dev.txt           # Зависимости для разработки
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Для удобного запуска
├── .dockerignore                  # Исключения для Docker
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD
├── src/
│   ├── __init__.py
│   ├── contrast_checker.py        # Основной модуль
│   ├── color_parser.py            # Парсинг CSS цветов
│   ├── html_parser.py             # Извлечение entity (BeautifulSoup)
│   ├── image_analyzer.py          # ML для доминирующих цветов
│   ├── wcag.py                    # Расчёт контраста и классификация
│   └── cli.py                     # CLI interface
├── tests/
│   ├── __init__.py
│   ├── test_color_parser.py
│   ├── test_html_parser.py
│   ├── test_image_analyzer.py
│   ├── test_wcag.py
│   └── test_integration.py
├── examples/
│   ├── slide_color_bg.json        # Пример: только цвета
│   ├── slide_with_image.json      # Пример: с картинкой
│   ├── slide_complex.json         # Пример: сложный случай
│   └── background.png             # Тестовое изображение
├── docs/
│   ├── ARCHITECTURE.md            # Архитектура решения
│   ├── ML_APPROACH.md             # Обоснование ML методов
│   └── API.md                     # Документация API
└── output/
    └── .gitkeep                   # Для выходных файлов
```

### 2. ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ
- Создай и активируй venv
- Все команды должны выполняться внутри venv
- В README добавь инструкции по активации для Linux/Mac/Windows

### 3. GIT WORKFLOW
Инициализируй Git с правильной структурой коммитов:
```bash
git init
git add .
git commit -m "Initial commit: project structure"
git add src/
git commit -m "feat: add core modules (color parser, HTML parser, WCAG calculator)"
git add tests/
git commit -m "test: add comprehensive unit tests"
git add Dockerfile docker-compose.yml
git commit -m "chore: add Docker configuration"
git add README.md docs/
git commit -m "docs: add comprehensive documentation"
```

### 4. DOCKER КОНФИГУРАЦИЯ

#### Dockerfile (multi-stage build):
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
COPY examples/ ./examples/
ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT ["python", "-m", "src.cli"]
CMD ["--help"]
```

#### docker-compose.yml:
```yaml
version: '3.8'
services:
  contrast-checker:
    build: .
    image: hse-contrast-checker:latest
    volumes:
      - ./examples:/app/examples:ro
      - ./output:/app/output
    environment:
      - PYTHONUNBUFFERED=1
```

### 5. ЗАВИСИМОСТИ

#### requirements.txt:
```
Pillow>=10.4.0
beautifulsoup4>=4.12.0
lxml>=5.1.0
numpy>=1.26.0
scikit-learn>=1.4.0
click>=8.1.0
```

#### requirements-dev.txt:
```
pytest>=8.0.0
pytest-cov>=4.1.0
black>=24.0.0
flake8>=7.0.0
mypy>=1.8.0
```

### 6. ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ К КОДУ

#### 6.1. HTML ПАРСИНГ (ОБЯЗАТЕЛЬНО BeautifulSoup, НЕ regex!)
```python
from bs4 import BeautifulSoup
import re

def extract_entities_robust(content_html: str) -> List[Dict[str, Any]]:
    """
    Извлекает все текстовые entity из HTML с помощью BeautifulSoup.
    
    Returns:
        List of dicts with: id, wrapper_style, spans_styles, text_content
    """
    soup = BeautifulSoup(content_html, 'lxml')
    entities = []
    
    for div in soup.find_all('div', id=re.compile(r'^text-')):
        entity_id = div.get('id')
        
        # Найти wrapper с геометрией
        wrapper = div.find(class_=re.compile(r'entity__wrapper'))
        wrapper_style = wrapper.get('style', '') if wrapper else ''
        
        # Собрать все span с стилями
        spans = div.find_all('span')
        spans_styles = [s.get('style', '') for s in spans if s.get('style')]
        
        # Извлечь весь текст для взвешивания
        text_content = div.get_text(strip=True)
        
        entities.append({
            'id': entity_id,
            'wrapper_style': wrapper_style,
            'spans_styles': spans_styles,
            'text_content': text_content,
            'raw_html': str(div)
        })
    
    return entities
```

#### 6.2. ML ДЛЯ ДОМИНИРУЮЩИХ ЦВЕТОВ (Два варианта!)

**Вариант A: Median-cut (Pillow ADAPTIVE) — быстрее**
```python
def dominant_colors_mediancut(img: Image.Image, bbox: Tuple[int,int,int,int], k: int=5):
    """
    Использует median-cut algorithm для квантизации палитры.
    Это ML-метод несупервизорного обучения.
    """
    region = img.crop(bbox)
    region = region.resize((min(150, region.width), min(150, region.height)), Image.LANCZOS)
    
    # Median-cut quantization
    pal_img = region.convert('P', palette=Image.ADAPTIVE, colors=k)
    palette = pal_img.getpalette()
    color_counts = pal_img.getcolors()
    
    # Преобразование в список (rgb, weight)
    total = sum(count for count, _ in color_counts)
    result = []
    for count, idx in sorted(color_counts, reverse=True):
        r, g, b = palette[idx*3:(idx+1)*3]
        result.append(((r, g, b), count / total))
    
    return result[:k]
```

**Вариант B: K-means (sklearn) — точнее для сложных случаев**
```python
from sklearn.cluster import KMeans
import numpy as np

def dominant_colors_kmeans(img: Image.Image, bbox: Tuple[int,int,int,int], k: int=5):
    """
    Использует K-means кластеризацию для определения доминирующих цветов.
    Стандартный ML-алгоритм unsupervised learning.
    """
    region = img.crop(bbox)
    region = region.resize((150, 150), Image.LANCZOS)
    
    # Преобразование в массив пикселей
    pixels = np.array(region).reshape(-1, 3)
    
    # K-means clustering
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Центры кластеров и их веса
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    counts = np.bincount(labels)
    weights = counts / len(labels)
    
    result = [(tuple(colors[i]), weights[i]) for i in range(k)]
    return sorted(result, key=lambda x: x[1], reverse=True)
```

**РЕАЛИЗУЙ ОБА ВАРИАНТА** и добавь CLI флаг `--ml-method {mediancut,kmeans}` для выбора!

#### 6.3. УЛУЧШЕННАЯ ОЦЕНКА COVERAGE ЦВЕТОВ
```python
def analyze_text_colors(spans_data: List[Dict], default_color: str) -> List[Tuple[Tuple[int,int,int], str, float]]:
    """
    Анализирует цвета текста с учётом font-size и длины текста.
    
    Returns:
        List of (rgb_tuple, css_color, weight)
    """
    if not spans_data:
        rgba = parse_css_color(default_color)
        return [(rgba.to_rgb_tuple(), default_color, 1.0)]
    
    weighted_colors = []
    
    for span in spans_data:
        style = parse_style(span['style'])
        
        # Цвет
        color_css = style.get('color', default_color)
        rgba = parse_css_color(color_css)
        
        # Размер шрифта
        font_size = parse_font_size_px(style.get('font-size', '16px')) or 16.0
        
        # Длина текста
        text_len = len(span.get('text', ''))
        
        # Вес = площадь текста (font_size × длина)
        weight = font_size * text_len
        
        weighted_colors.append((rgba.to_rgb_tuple(), color_css, weight))
    
    # Нормализация весов
    total_weight = sum(w for _, _, w in weighted_colors)
    if total_weight > 0:
        weighted_colors = [(rgb, css, w/total_weight) for rgb, css, w in weighted_colors]
    
    return weighted_colors
```

#### 6.4. РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ
```python
def suggest_fixes(
    contrast_ratio: float,
    text_rgb: Tuple[int, int, int],
    bg_rgb: Tuple[int, int, int],
    font_size_px: float,
    font_weight: str
) -> List[Dict[str, Any]]:
    """
    Генерирует рекомендации по улучшению контрастности.
    
    Returns:
        List of suggestions with 'type', 'description', 'new_value', 'expected_ratio'
    """
    suggestions = []
    target_ratio = 4.5  # AA normal
    
    if contrast_ratio >= target_ratio:
        return suggestions
    
    # 1. Инверсия цвета текста
    inverted_text = (255 - text_rgb[0], 255 - text_rgb[1], 255 - text_rgb[2])
    inv_ratio = compute_contrast_ratio(inverted_text, bg_rgb)
    if inv_ratio >= target_ratio:
        suggestions.append({
            'type': 'invert_text_color',
            'description': 'Инвертировать цвет текста',
            'new_value': f'#{inverted_text[0]:02x}{inverted_text[1]:02x}{inverted_text[2]:02x}',
            'expected_ratio': round(inv_ratio, 2)
        })
    
    # 2. Изменить на белый/чёрный
    for new_text, name in [((0, 0, 0), 'black'), ((255, 255, 255), 'white')]:
        new_ratio = compute_contrast_ratio(new_text, bg_rgb)
        if new_ratio >= target_ratio:
            suggestions.append({
                'type': 'change_text_color',
                'description': f'Изменить цвет текста на {name}',
                'new_value': f'#{new_text[0]:02x}{new_text[1]:02x}{new_text[2]:02x}',
                'expected_ratio': round(new_ratio, 2)
            })
    
    # 3. Затемнить фон
    for factor in [0.8, 0.6, 0.4]:
        darkened_bg = tuple(int(c * factor) for c in bg_rgb)
        dark_ratio = compute_contrast_ratio(text_rgb, darkened_bg)
        if dark_ratio >= target_ratio:
            suggestions.append({
                'type': 'darken_background',
                'description': f'Затемнить фон на {int((1-factor)*100)}%',
                'new_value': f'rgb({darkened_bg[0]}, {darkened_bg[1]}, {darkened_bg[2]})',
                'expected_ratio': round(dark_ratio, 2)
            })
            break
    
    # 4. Увеличить размер шрифта (для перехода в large text)
    if font_size_px < 24:
        suggestions.append({
            'type': 'increase_font_size',
            'description': 'Увеличить размер шрифта до ≥24px (порог AA large: 3:1)',
            'new_value': '24px',
            'expected_ratio': contrast_ratio  # Остаётся тот же
        })
    
    # 5. Добавить тень/обводку
    suggestions.append({
        'type': 'add_text_shadow',
        'description': 'Добавить тень текста для улучшения читаемости',
        'new_value': 'text-shadow: 0 0 4px rgba(0,0,0,0.8)',
        'expected_ratio': None  # Не вычисляется
    })
    
    return suggestions
```

#### 6.5. HTML ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ
```python
def generate_html_report(result: Dict[str, Any], output_path: str):
    """
    Генерирует HTML-отчёт с визуальными примерами и статусами WCAG.
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contrast Analysis Report - Slide {result['slide_id']}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
            h1 {{ color: #333; }}
            .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .entity-card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .status-pass {{ color: #28a745; font-weight: bold; }}
            .status-fail {{ color: #dc3545; font-weight: bold; }}
            .preview-box {{ display: inline-block; padding: 20px 40px; margin: 10px; border-radius: 4px; font-size: 18px; }}
            .wcag-badges {{ display: flex; gap: 10px; margin: 10px 0; }}
            .badge {{ padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
            .badge-pass {{ background: #28a745; color: white; }}
            .badge-fail {{ background: #dc3545; color: white; }}
            .suggestions {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-top: 15px; }}
            .suggestion-item {{ margin: 8px 0; padding: 8px; background: white; border-radius: 4px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: 600; }}
        </style>
    </head>
    <body>
        <h1>🎨 Contrast Analysis Report</h1>
        
        <div class="summary">
            <h2>Slide #{result['slide_id']}</h2>
            <p><strong>Background:</strong> {result['background']['source']}</p>
            <p><strong>Effective Background RGB:</strong> 
                <span style="display: inline-block; width: 20px; height: 20px; background: rgb({result['background']['effective_rgb'][0]}, {result['background']['effective_rgb'][1]}, {result['background']['effective_rgb'][2]}); border: 1px solid #ccc; vertical-align: middle;"></span>
                rgb({result['background']['effective_rgb'][0]}, {result['background']['effective_rgb'][1]}, {result['background']['effective_rgb'][2]})
            </p>
            <p><strong>Total Entities:</strong> {len(result['entities'])}</p>
        </div>
    """
    
    for ent in result['entities']:
        wcag = ent['contrast']['wcag']
        status = "✅ PASS" if wcag['AA_normal'] else "❌ FAIL"
        status_class = "status-pass" if wcag['AA_normal'] else "status-fail"
        
        html += f"""
        <div class="entity-card">
            <h3>{ent['id']} <span class="{status_class}">{status}</span></h3>
            
            <table>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Contrast Ratio</td>
                    <td><strong>{ent['contrast']['min_ratio']}:1</strong></td>
                </tr>
                <tr>
                    <td>Font Size</td>
                    <td>{ent['font']['size_px']}px</td>
                </tr>
                <tr>
                    <td>Font Weight</td>
                    <td>{ent['font']['weight']}</td>
                </tr>
            </table>
            
            <div class="wcag-badges">
                <span class="badge badge-{'pass' if wcag['AA_normal'] else 'fail'}">
                    AA Normal: {'✓' if wcag['AA_normal'] else '✗'}
                </span>
                <span class="badge badge-{'pass' if wcag['AA_large'] else 'fail'}">
                    AA Large: {'✓' if wcag['AA_large'] else '✗'}
                </span>
                <span class="badge badge-{'pass' if wcag['AAA'] else 'fail'}">
                    AAA: {'✓' if wcag['AAA'] else '✗'}
                </span>
            </div>
            
            <h4>Visual Previews:</h4>
            <div>
        """
        
        bg_rgb = result['background']['effective_rgb']
        for tc in ent['text_colors']:
            html += f"""
                <div class="preview-box" style="background: rgb({bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]}); color: {tc['css']}; font-size: {ent['font']['size_px']}px; font-weight: {ent['font']['weight']};">
                    Sample Text ({tc['css']})
                </div>
            """
        
        html += """
            </div>
        """
        
        # Добавить рекомендации, если провал
        if not wcag['AA_normal'] and 'suggestions' in ent:
            html += """
            <div class="suggestions">
                <h4>💡 Recommendations:</h4>
            """
            for sug in ent['suggestions']:
                html += f"""
                <div class="suggestion-item">
                    <strong>{sug['type']}:</strong> {sug['description']} 
                    → <code>{sug['new_value']}</code>
                    {f"(Expected ratio: {sug['expected_ratio']}:1)" if sug.get('expected_ratio') else ""}
                </div>
                """
            html += "</div>"
        
        html += """
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
```

### 7. CLI INTERFACE (click библиотека)

```python
import click
from pathlib import Path

@click.command()
@click.option('--slide-json', required=True, type=click.Path(exists=True), 
              help='Path to slide JSON file')
@click.option('--slide-index', type=int, default=None,
              help='If JSON is array, index of slide to analyze')
@click.option('--bg-image', type=click.Path(exists=True), default=None,
              help='Optional background image file')
@click.option('--ml-method', type=click.Choice(['mediancut', 'kmeans']), default='mediancut',
              help='ML method for dominant colors extraction')
@click.option('--k-colors', type=int, default=5,
              help='Number of dominant colors to extract')
@click.option('--out-json', type=click.Path(), default='output/result.json',
              help='Output JSON file path')
@click.option('--out-html', type=click.Path(), default='output/report.html',
              help='Output HTML report path')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def main(slide_json, slide_index, bg_image, ml_method, k_colors, out_json, out_html, verbose):
    """
    HSE ML Contrast Checker - Analyze text/background contrast using ML
    """
    if verbose:
        click.echo(f"Loading slide from: {slide_json}")
        click.echo(f"ML method: {ml_method}")
    
    # Load and analyze
    try:
        result = analyze_slide(...)
        
        # Save JSON
        Path(out_json).parent.mkdir(parents=True, exist_ok=True)
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Generate HTML report
        generate_html_report(result, out_html)
        
        click.secho(f"✓ Analysis complete!", fg='green')
        click.echo(f"  JSON: {out_json}")
        click.echo(f"  HTML: {out_html}")
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()

if __name__ == '__main__':
    main()
```

### 8. ТЕСТЫ (pytest)

Создай тесты для каждого модуля:

```python
# tests/test_color_parser.py
import pytest
from src.color_parser import parse_css_color, blend_over, RGBA

def test_hex8_parsing():
    rgba = parse_css_color('#4FAEFF26')
    assert rgba.r == 79
    assert rgba.g == 174
    assert rgba.b == 255
    assert abs(rgba.a - 0.149) < 0.01

def test_blend_transparency():
    over = RGBA(79, 174, 255, 0.149)
    under = (255, 255, 255)
    result = blend_over(over, under)
    assert result == (229, 243, 255)

def test_hsl_to_rgb():
    rgba = parse_css_color('hsl(200, 100%, 50%)')
    assert rgba.r == 0
    assert rgba.g == 170  # Приблизительно
    assert rgba.b == 255

# tests/test_wcag.py
def test_contrast_black_white():
    from src.wcag import contrast_ratio
    ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
    assert abs(ratio - 21.0) < 0.1

def test_wcag_classification():
    from src.wcag import classify_wcag
    wcag = classify_wcag(18.6, 52, 'normal')
    assert wcag['AA_normal'] == True
    assert wcag['AAA'] == True
```

### 9. ДОКУМЕНТАЦИЯ

#### README.md должен содержать:

1. **Badges**: Build status, coverage, license
2. **Описание проекта** с примером входа/выхода
3. **Установка**: venv, pip, Docker
4. **Quick Start**: примеры команд
5. **Архитектура**: диаграмма модулей
6. **ML Approach**: объяснение median-cut и K-means
7. **WCAG Standards**: таблица порогов
8. **Development**: как запустить тесты, линтеры
9. **Docker Usage**: команды docker-compose
10. **API Reference**: ссылка на docs/API.md

#### docs/ML_APPROACH.md должен объяснять:

1. Почему выбран median-cut/K-means
2. Сравнение методов (скорость vs точность)
3. Альтернативы (ColorThief, CNN)
4. Обоснование, почему не нужна нейросеть
5. Математика median-cut algorithm

### 10. CI/CD (.github/workflows/ci.yml)

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt -r requirements-dev.txt
    
    - name: Lint with flake8
      run: flake8 src tests --max-line-length=120
    
    - name: Type check with mypy
      run: mypy src --ignore-missing-imports
    
    - name: Test with pytest
      run: pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  docker:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t hse-contrast-checker:test .
    
    - name: Test Docker image
      run: |
        docker run hse-contrast-checker:test --help
```

### 11. ПРИМЕРЫ JSON ФАЙЛОВ

Создай 3 примера в `examples/`:

1. **slide_color_bg.json** - только base_color
2. **slide_with_image.json** - с фоновой картинкой
3. **slide_complex.json** - полупрозрачные слои + картинка + множественные цвета

### 12. DOCKER КОМАНДЫ ДЛЯ README

```bash
# Build image
docker build -t hse-contrast-checker .

# Run analysis (color-only)
docker run -v $(pwd)/examples:/app/examples -v $(pwd)/output:/app/output \
  hse-contrast-checker --slide-json /app/examples/slide_color_bg.json

# Run with docker-compose
docker-compose run contrast-checker --slide-json /app/examples/slide_with_image.json --bg-image /app/examples/background.png

# Interactive shell
docker run -it --entrypoint /bin/bash hse-contrast-checker
```

### 13. ФИНАЛЬНЫЙ ЧЕКЛИСТ (для оценки 10/10)

- [ ] Структура проекта как описано выше
- [ ] Git репозиторий с осмысленными коммитами
- [ ] Виртуальное окружение (venv)
- [ ] Dockerfile с multi-stage build
- [ ] docker-compose.yml
- [ ] BeautifulSoup для HTML парсинга (НЕ regex!)
- [ ] Два ML метода: median-cut + K-means с выбором через CLI
- [ ] Улучшенный расчёт coverage цветов (font-size × длина текста)
- [ ] Функция suggest_fixes() с конкретными рекомендациями
- [ ] HTML визуализация результатов
- [ ] CLI на click с --help, --verbose, --ml-method
- [ ] Comprehensive тесты (pytest) с coverage >80%
- [ ] README.md с badges, примерами, диаграммами
- [ ] docs/ML_APPROACH.md с обоснованием ML методов
- [ ] docs/ARCHITECTURE.md с описанием модулей
- [ ] .github/workflows/ci.yml для CI/CD
- [ ] Все зависимости в requirements.txt
- [ ] .gitignore для Python + Docker + IDE
- [ ] LICENSE файл (MIT)
- [ ] Type hints (mypy проверка)
- [ ] Docstrings для всех функций
- [ ] Error handling с понятными сообщениями
- [ ] Примеры JSON в examples/

## ВАЖНО: ПОРЯДОК ВЫПОЛНЕНИЯ

1. Сначала создай структуру проекта и Git init
2. Потом создай виртуальное окружение и установи зависимости
3. Реализуй модули в src/ по порядку: color_parser → html_parser → image_analyzer → wcag → cli
4. Напиши тесты для каждого модуля сразу после его реализации
5. Создай примеры JSON файлов
6. Реализуй HTML визуализацию
7. Настрой Docker
8. Напиши документацию
9. Настрой CI/CD
10. Финальный прогон всех тестов

## СТИЛЬ КОДА

- Type hints для всех функций
- Docstrings в Google style
- Black для форматирования (line length 120)
- flake8 для линтинга
- mypy для type checking
- pytest для тестов

## ДОПОЛНИТЕЛЬНЫЕ ФИШКИ ДЛЯ "ВАУ-ЭФФЕКТА"

1. Progress bar при обработке больших изображений (tqdm)
2. Поддержка batch processing (массив слайдов)
3. Export в CSV для анализа в Excel
4. Matplotlib графики распределения контрастности
5. Интеграция с pre-commit hooks
6. Makefile для удобных команд (make test, make docker, make docs)

---

ВЫПОЛНИ ВСЁ ЭТО ПОШАГОВО. НАЧНИ С СОЗДАНИЯ СТРУКТУРЫ ПРОЕКТА И GIT INIT.
ИСПОЛЬЗУЙ ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ С САМОГО НАЧАЛА.
ДОКЕР ДОЛЖЕН РАБОТАТЬ СРАЗУ ПОСЛЕ РЕАЛИЗАЦИИ ОСНОВНОГО ФУНКЦИОНАЛА.

Я ЖДУ PRODUCTION-READY РЕШЕНИЕ, КОТОРОЕ МОЖНО ПОКАЗАТЬ НА ЗАЩИТЕ И ПОЛУЧИТЬ 10/10!
```

---

## 📋 КРАТКАЯ ПАМЯТКА ДЛЯ ЗАПУСКА CLAUDE CODE

После того как Claude Code создаст проект, вы сможете:

```bash
# Активировать venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установить зависимости
pip install -r requirements.txt -r requirements-dev.txt

# Запустить тесты
pytest tests/ -v --cov=src

# Запустить линтеры
black src tests
flake8 src tests
mypy src

# Локальный запуск
python -m src.cli --slide-json examples/slide_color_bg.json

# Docker build
docker build -t hse-contrast-checker .

# Docker run
docker-compose run contrast-checker --slide-json /app/examples/slide_with_image.json --out-json /app/output/result.json --out-html /app/output/report.html

# Git коммиты
git add .
git commit -m "feat: complete implementation with ML, tests, Docker, CI/CD"
git push origin main
```

---

**Этот промпт даст вам проект, который:**
✅ Использует настоящее ML (median-cut + K-means)  
✅ Имеет production-ready структуру  
✅ Покрыт тестами  
✅ Работает в Docker  
✅ Имеет CI/CD  
✅ Полностью документирован  
✅ Генерирует красивые HTML отчёты  
✅ Даёт рекомендации по исправлению  
✅ Гарантирует оценку 10/10 🎉