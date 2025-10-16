# 📖 API Документация

Полная справка по API модулей HSE ML Contrast Checker.

## Содержание

- [color_parser](#color_parser)
- [html_parser](#html_parser)
- [image_analyzer](#image_analyzer)
- [wcag](#wcag)
- [contrast_checker](#contrast_checker)
- [report_generator](#report_generator)
- [webapp (Web API)](#webapp-web-api)
- [batch_analyzer](#batch_analyzer)
- [slide_scraper](#slide_scraper)

---

## color_parser

Модуль для парсинга и манипуляций с CSS цветами.

### Классы

#### `RGBA`

Представление цвета с альфа-каналом.

```python
@dataclass
class RGBA:
    r: int      # 0-255
    g: int      # 0-255
    b: int      # 0-255
    a: float    # 0.0-1.0
```

**Методы:**

- `to_rgb_tuple() -> Tuple[int, int, int]` - Конвертация в RGB кортеж

### Функции

#### `parse_css_color(color: str) -> RGBA`

Парсит CSS строку цвета в объект RGBA.

**Параметры:**
- `color` (str): CSS строка цвета

**Возвращает:**
- `RGBA`: Объект цвета

**Поддерживаемые форматы:**
- Hex: `#RGB`, `#RRGGBB`, `#RRGGBBAA`
- RGB: `rgb(r, g, b)`, `rgba(r, g, b, a)`
- HSL: `hsl(h, s%, l%)`, `hsla(h, s%, l%, a)`
- Именованные: `white`, `black`, `red`, `transparent`, и др.

**Примеры:**
```python
>>> parse_css_color('#ff0000')
RGBA(r=255, g=0, b=0, a=1.0)

>>> parse_css_color('rgba(100, 150, 200, 0.5)')
RGBA(r=100, g=150, b=200, a=0.5)

>>> parse_css_color('hsl(120, 100%, 50%)')
RGBA(r=0, g=255, b=0, a=1.0)
```

#### `blend_over(rgba: RGBA, bg_rgb: Tuple[int, int, int]) -> Tuple[int, int, int]`

Альфа-композитинг RGBA цвета над RGB фоном.

**Параметры:**
- `rgba` (RGBA): Цвет переднего плана с альфой
- `bg_rgb` (Tuple[int, int, int]): Цвет фона

**Возвращает:**
- `Tuple[int, int, int]`: Результирующий непрозрачный RGB

**Формула:**
```
result = rgba.rgb * rgba.a + bg_rgb * (1 - rgba.a)
```

**Пример:**
```python
>>> fg = RGBA(255, 0, 0, 0.5)  # Полупрозрачный красный
>>> bg = (255, 255, 255)        # Белый
>>> blend_over(fg, bg)
(255, 127, 127)  # Розовый
```

#### `hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]`

Конвертация HSL в RGB.

**Параметры:**
- `h` (float): Оттенок 0-360
- `s` (float): Насыщенность 0-1
- `l` (float): Яркость 0-1

**Возвращает:**
- `Tuple[int, int, int]`: RGB значения

#### `parse_font_size_px(font_size: str) -> Optional[float]`

Парсит размер шрифта в пиксели.

**Поддерживаемые единицы:**
- `px`: Пиксели (без изменений)
- `pt`: Пункты (1pt = 1.333px)
- `em/rem`: Относительные единицы (базовые 16px)

**Пример:**
```python
>>> parse_font_size_px('14px')
14.0
>>> parse_font_size_px('12pt')
16.0
>>> parse_font_size_px('1.5em')
24.0
```

---

## html_parser

Модуль для извлечения текстовых элементов из HTML.

### Функции

#### `extract_entities(content_html: str) -> List[Dict[str, Any]]`

Извлекает текстовые элементы из HTML содержимого слайда.

**Параметры:**
- `content_html` (str): HTML содержимое

**Возвращает:**
- `List[Dict]`: Список словарей сущностей с ключами:
  - `id` (str): ID элемента (например, "text-123")
  - `wrapper_style` (str): CSS стиль обертки
  - `spans` (List[Dict]): Список span элементов
  - `text_content` (str): Полный текст
  - `raw_html` (str): Исходный HTML

**Пример:**
```python
>>> html = '<div id="text-1" style="..."><span style="color: red">Hello</span></div>'
>>> entities = extract_entities(html)
>>> entities[0]['id']
'text-1'
```

#### `extract_font_info(entity: Dict[str, Any]) -> Dict[str, Any]`

Извлекает информацию о шрифте из элемента.

**Параметры:**
- `entity` (Dict): Словарь элемента из `extract_entities()`

**Возвращает:**
- `Dict` с ключами:
  - `size_px` (float): Размер шрифта в пикселях
  - `weight` (str): Вес шрифта ('normal', 'bold', '700', и т.д.)
  - `is_large` (bool): Квалифицируется ли как "крупный текст" по WCAG

**Критерии крупного текста:**
- ≥24px любого веса
- ≥18.67px с весом ≥700

---

## image_analyzer

ML модуль для извлечения доминирующих цветов.

### Функции

#### `dominant_colors_mediancut(img: Image.Image, bbox: Optional[Tuple[int, int, int, int]] = None, k: int = 5) -> List[Tuple[Tuple[int, int, int], float]]`

Извлечение доминирующих цветов используя алгоритм Median-cut.

**Параметры:**
- `img` (Image.Image): PIL изображение (RGB режим)
- `bbox` (Optional[Tuple]): Ограничивающий прямоугольник (left, top, right, bottom)
- `k` (int): Количество доминирующих цветов

**Возвращает:**
- `List[Tuple[RGB, weight]]`: Список кортежей ((r,g,b), вес), отсортированных по убыванию веса

**Пример:**
```python
>>> img = Image.open('background.png')
>>> colors = dominant_colors_mediancut(img, k=3)
>>> colors[0]
((245, 123, 67), 0.42)  # Самый доминирующий: 42% пикселей
```

#### `dominant_colors_kmeans(img: Image.Image, bbox: Optional[Tuple[int, int, int, int]] = None, k: int = 5, random_state: int = 42) -> List[Tuple[Tuple[int, int, int], float]]`

Извлечение доминирующих цветов используя K-means кластеризацию.

**Параметры:**
- `img` (Image.Image): PIL изображение
- `bbox` (Optional[Tuple]): Ограничивающий прямоугольник
- `k` (int): Количество кластеров
- `random_state` (int): Зерно для воспроизводимости

**Возвращает:**
- `List[Tuple[RGB, weight]]`: Список кортежей (цвет, вес)

**Пример:**
```python
>>> colors = dominant_colors_kmeans(img, k=5, random_state=42)
>>> colors[0]
((242, 118, 71), 0.38)
```

#### `get_dominant_color_simple(img: Image.Image, method: str = 'mediancut') -> Tuple[int, int, int]`

Получить единственный самый доминирующий цвет.

**Параметры:**
- `img` (Image.Image): PIL изображение
- `method` (str): 'mediancut' или 'kmeans'

**Возвращает:**
- `Tuple[int, int, int]`: RGB кортеж самого доминирующего цвета

---

## wcag

Модуль для расчета контрастности WCAG 2.2.

### Функции

#### `relative_luminance(rgb: Tuple[int, int, int]) -> float`

Вычисление относительной яркости RGB цвета.

**Формула WCAG 2.2:**
```
L = 0.2126 * R + 0.7152 * G + 0.0722 * B
```

**Параметры:**
- `rgb` (Tuple[int, int, int]): RGB кортеж (0-255)

**Возвращает:**
- `float`: Относительная яркость (0.0-1.0)

**Пример:**
```python
>>> relative_luminance((255, 255, 255))  # Белый
1.0
>>> relative_luminance((0, 0, 0))  # Черный
0.0
```

#### `contrast_ratio(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float`

Вычисление коэффициента контрастности между двумя цветами.

**Формула WCAG 2.2:**
```
ratio = (L1 + 0.05) / (L2 + 0.05)
где L1 - яркость более светлого цвета
```

**Параметры:**
- `color1` (Tuple): RGB кортеж
- `color2` (Tuple): RGB кортеж

**Возвращает:**
- `float`: Коэффициент контрастности (1.0-21.0)

**Пример:**
```python
>>> contrast_ratio((0, 0, 0), (255, 255, 255))
21.0  # Максимальная контрастность
>>> contrast_ratio((128, 128, 128), (128, 128, 128))
1.0   # Одинаковый цвет
```

#### `classify_wcag(ratio: float, font_size_px: float, font_weight: str) -> Dict[str, bool]`

Классификация коэффициента контрастности по стандартам WCAG 2.2.

**Уровни WCAG:**
- AA Normal: 4.5:1
- AA Large: 3:1
- AAA Normal: 7:1
- AAA Large: 4.5:1

**Параметры:**
- `ratio` (float): Коэффициент контрастности
- `font_size_px` (float): Размер шрифта в пикселях
- `font_weight` (str): Вес шрифта

**Возвращает:**
- `Dict[str, bool]` с ключами:
  - `AA_normal` (bool): Проходит AA для обычного текста
  - `AA_large` (bool): Проходит AA для крупного текста
  - `AAA` (bool): Проходит AAA
  - `is_large_text` (bool): Квалифицируется как крупный текст

**Пример:**
```python
>>> classify_wcag(4.6, 16, 'normal')
{'AA_normal': True, 'AA_large': True, 'AAA': False, 'is_large_text': False}
```

#### `suggest_fixes(current_ratio: float, text_rgb: Tuple[int, int, int], bg_rgb: Tuple[int, int, int], font_size_px: float, font_weight: str) -> List[Dict[str, Any]]`

Генерация рекомендаций по улучшению контрастности.

**Параметры:**
- `current_ratio` (float): Текущий коэффициент контрастности
- `text_rgb` (Tuple): RGB цвета текста
- `bg_rgb` (Tuple): RGB цвета фона
- `font_size_px` (float): Размер шрифта
- `font_weight` (str): Вес шрифта

**Возвращает:**
- `List[Dict]`: Список рекомендаций с ключами:
  - `type` (str): Тип рекомендации
  - `description` (str): Читаемое описание
  - `new_value` (str): Предлагаемое CSS значение
  - `expected_ratio` (float): Ожидаемый новый коэффициент

**Типы рекомендаций:**
- `invert_text_color`: Инвертировать цвет текста
- `change_text_color`: Изменить текст на черный/белый
- `darken_background`: Затемнить фон
- `lighten_background`: Осветлить фон
- `increase_font_size`: Увеличить размер шрифта

---

## contrast_checker

Главный модуль оркестрации анализа.

### Функции

#### `analyze_slide(slide_json_path: str, slide_index: Optional[int] = None, bg_image_path: Optional[str] = None, ml_method: str = 'mediancut', k_colors: int = 5) -> Dict[str, Any]`

Анализ контрастности для слайда.

**Параметры:**
- `slide_json_path` (str): Путь к JSON файлу слайда
- `slide_index` (Optional[int]): Индекс слайда, если JSON массив
- `bg_image_path` (Optional[str]): Путь к фоновому изображению
- `ml_method` (str): ML метод ('mediancut' или 'kmeans')
- `k_colors` (int): Количество доминирующих цветов для извлечения

**Возвращает:**
- `Dict[str, Any]`: Результат анализа с ключами:
  - `slide_id` (str): ID слайда
  - `background` (Dict): Информация о фоне
  - `ml_method` (str): Использованный ML метод
  - `entities` (List[Dict]): Результаты для каждого элемента
  - `summary` (Dict): Сводная статистика

**Выбрасывает:**
- `FileNotFoundError`: Если файл не найден
- `ValueError`: Если JSON невалиден

**Пример:**
```python
>>> result = analyze_slide(
...     slide_json_path='examples/slide.json',
...     bg_image_path='examples/bg.png',
...     ml_method='kmeans',
...     k_colors=5
... )
>>> result['summary']
{'total_entities': 3, 'passed_AA_normal': 2, 'failed_AA_normal': 1}
```

---

## report_generator

Модуль для генерации HTML отчетов.

### Функции

#### `generate_html_report(result: Dict[str, Any], output_path: str) -> None`

Генерация HTML отчета с визуальными примерами и WCAG значками.

**Параметры:**
- `result` (Dict): Словарь результата из `analyze_slide()`
- `output_path` (str): Путь для сохранения HTML отчета

**Возвращает:**
- None (записывает в файл)

**Особенности отчета:**
- Сводная информация слайда
- Карточки для каждого элемента
- Визуальные примеры цветовых комбинаций
- WCAG значки (AA Normal, AA Large, AAA)
- Рекомендации для неудачных элементов

**Пример:**
```python
>>> generate_html_report(result, 'output/report.html')
# Создает красивый HTML отчет
```

---

## Типичные рабочие процессы

### Полный анализ

```python
from src.contrast_checker import analyze_slide
from src.report_generator import generate_html_report
import json

# 1. Анализ слайда
result = analyze_slide(
    slide_json_path='examples/slide.json',
    bg_image_path='examples/background.png',
    ml_method='kmeans',
    k_colors=5
)

# 2. Сохранение JSON
with open('output/result.json', 'w') as f:
    json.dump(result, f, indent=2)

# 3. Генерация HTML отчета
generate_html_report(result, 'output/report.html')

# 4. Проверка соответствия
if result['summary']['failed_AA_normal'] > 0:
    print(f"Предупреждение: {result['summary']['failed_AA_normal']} элементов не прошли WCAG AA")
```

### Пользовательский анализ цветов

```python
from PIL import Image
from src.image_analyzer import dominant_colors_kmeans
from src.wcag import contrast_ratio, classify_wcag

# 1. Извлечение доминирующих цветов
img = Image.open('background.png')
bg_colors = dominant_colors_kmeans(img, k=5)
bg_rgb = bg_colors[0][0]  # Самый доминирующий

# 2. Определенный цвет текста
text_rgb = (0, 0, 0)  # Черный

# 3. Проверка контрастности
ratio = contrast_ratio(text_rgb, bg_rgb)
wcag = classify_wcag(ratio, font_size_px=16, font_weight='normal')

print(f"Коэффициент: {ratio:.2f}")
print(f"Проходит AA: {wcag['AA_normal']}")
```

---

## webapp (Web API)

FastAPI веб-приложение для анализа контрастности через HTTP API.

### Endpoints

#### `GET /`

Главная страница веб-интерфейса.

**Возвращает:**
- HTML страницу с веб-интерфейсом

#### `GET /health`

Health check endpoint для проверки состояния сервиса.

**Возвращает:**
```json
{
  "status": "ok",
  "service": "HSE ML Contrast Checker"
}
```

#### `POST /api/analyze-url`

Анализ слайдов из URL с использованием Selenium.

**Параметры (Form Data):**
- `url` (str, обязательный): URL презентации Diaclass
- `ml_method` (str, optional): "mediancut" или "kmeans" (default: "mediancut")
- `slide_mode` (str, optional): "single" или "all" (default: "single")
- `slide_index` (int, optional): Индекс слайда для режима "single" (default: 1)

**Возвращает:**
```json
{
  "success": true,
  "session_id": "abc123",
  "total_slides": 3,
  "results": [
    {
      "slide_id": "slide-001",
      "slide_number": 1,
      "summary": {
        "total_entities": 5,
        "passed_AA_normal": 4,
        "failed_AA_normal": 1
      },
      "report_url": "/results/abc123/report_001.html",
      "json_url": "/results/abc123/result_001.json"
    }
  ]
}
```

**Ошибки:**
- `400`: Не удалось извлечь слайды
- `500`: Ошибка при анализе

#### `POST /api/analyze-file`

Анализ загруженного HTML файла.

**Параметры (Multipart Form Data):**
- `file` (File, обязательный): HTML файл презентации
- `ml_method` (str, optional): "mediancut" или "kmeans" (default: "mediancut")
- `slide_mode` (str, optional): "single" или "all" (default: "single")
- `slide_index` (int, optional): Индекс слайда (default: 1)

**Возвращает:**
- Аналогично `/api/analyze-url`

**Ошибки:**
- `400`: Неверный тип файла (только HTML)
- `500`: Ошибка при анализе

#### `GET /api/result/{session_id}/{filename}`

Получение результатов анализа.

**Параметры (Path):**
- `session_id` (str): ID сессии
- `filename` (str): Имя файла (report_XXX.html или result_XXX.json)

**Возвращает:**
- HTML отчет или JSON файл

**Ошибки:**
- `404`: Файл не найден

### Пример использования

```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Анализ по URL
data = {
    'url': 'https://app.diaclass.ru/share/xxx',
    'ml_method': 'kmeans',
    'slide_mode': 'all'
}
response = requests.post('http://localhost:8000/api/analyze-url', data=data)
result = response.json()

print(f"Проанализировано слайдов: {result['total_slides']}")
for slide_result in result['results']:
    print(f"Слайд {slide_result['slide_number']}: {slide_result['report_url']}")
```

---

## batch_analyzer

Модуль для массовой обработки множества слайдов.

### Функции

#### `analyze_slide_batch(slides_dir, output_dir, ml_method, verbose)`

Анализирует все JSON файлы слайдов в директории.

**Параметры:**
- `slides_dir` (str): Директория с JSON файлами слайдов
- `output_dir` (str): Директория для сохранения результатов
- `ml_method` (str): ML метод ("mediancut" или "kmeans")
- `verbose` (bool): Подробный вывод

**Возвращает:**
- `List[Dict]`: Список результатов анализа

**Пример:**
```python
from src.batch_analyzer import analyze_slide_batch

results = analyze_slide_batch(
    slides_dir='examples/slides',
    output_dir='output/batch',
    ml_method='kmeans',
    verbose=True
)

print(f"Успешно проанализировано: {len([r for r in results if 'error' not in r])}")
```

---

## slide_scraper

Модули для извлечения слайдов из HTML презентаций.

### slide_scraper.py (Базовый)

#### `scrape_slide_from_file(file_path, output_path, slide_id)`

Извлекает данные слайда из HTML файла.

**Параметры:**
- `file_path` (str): Путь к HTML файлу
- `output_path` (str, optional): Путь для сохранения JSON
- `slide_id` (str, optional): ID слайда

**Возвращает:**
- `Dict`: Данные слайда в формате JSON

### slide_scraper_advanced.py (Продвинутый)

#### `scrape_all_slides_from_url(url, output_dir, use_selenium, slide_index)`

Извлекает слайды из URL с поддержкой Selenium.

**Параметры:**
- `url` (str): URL презентации
- `output_dir` (str): Директория для сохранения
- `use_selenium` (bool): Использовать Selenium
- `slide_index` (int, optional): Извлечь конкретный слайд

**Возвращает:**
- `List[Dict]`: Список данных слайдов

**Пример:**
```python
from src.slide_scraper_advanced import scrape_all_slides_from_url

# Извлечь все слайды
slides = scrape_all_slides_from_url(
    url='https://app.diaclass.ru/share/xxx',
    output_dir='examples/slides',
    use_selenium=True
)

# Извлечь только слайд 5
slides = scrape_all_slides_from_url(
    url='https://app.diaclass.ru/share/xxx',
    output_dir='examples/slides',
    use_selenium=True,
    slide_index=5
)
```

---

## Обработка ошибок

### Распространенные исключения

```python
try:
    result = analyze_slide('slide.json')
except FileNotFoundError:
    print("JSON файл слайда не найден")
except ValueError as e:
    print(f"Невалидный JSON: {e}")
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
```

---

**Сопровождающий**: HSE ML Team
**Версия**: 1.1.0
**Последнее обновление**: Октябрь 2025

