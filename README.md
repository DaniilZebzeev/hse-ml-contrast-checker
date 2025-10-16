# 🎨 HSE ML Contrast Checker

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker Image](https://img.shields.io/docker/v/danilzebzeev/hse-contrast-checker?label=docker&logo=docker)](https://hub.docker.com/r/danilzebzeev/hse-contrast-checker)

Production-ready Python инструмент для анализа контрастности текста и фона согласно стандарту **WCAG 2.2** с использованием **машинного обучения**.

## 📋 Обзор

Этот инструмент анализирует контрастность между текстом и фоном в презентационных слайдах, используя ML алгоритмы для извлечения доминирующих цветов и расчета соответствия WCAG.

### ✨ Ключевые возможности

- ✅ **Соответствие WCAG 2.2**: Точный расчет контрастности по стандарту WCAG
- 🤖 **ML-алгоритмы**: Два алгоритма обучения без учителя для извлечения цветов:
  - **Median-cut** (быстрее, Pillow ADAPTIVE)
  - **K-means кластеризация** (точнее, scikit-learn)
- 🌐 **Веб-интерфейс**: Flask веб-приложение с drag-and-drop загрузкой HTML/JSON
- 📦 **Batch обработка**: Анализ нескольких слайдов одной командой
- 🔍 **Продвинутый scraper**: Автоматическое извлечение слайдов из HTML презентаций
- 📊 **HTML отчеты**: Визуальные отчеты с рекомендациями и примерами цветов
- 🐳 **Docker готов**: Включен multi-stage Docker build
- 🧪 **Хорошо протестирован**: Комплексный набор тестов с pytest
- 📝 **Типобезопасен**: Полные type hints и проверка mypy
- 🎯 **CLI интерфейс**: Удобный инструмент командной строки

## 🚀 Быстрый старт

### Вариант 1: Docker Hub (рекомендуется)

**Не нужно клонировать репозиторий или устанавливать зависимости!**

```bash
# Скачать готовый образ
docker pull danilzebzeev/hse-contrast-checker:latest

# Запустить анализ
docker run -v $(pwd)/output:/app/output \
  danilzebzeev/hse-contrast-checker:latest \
  --slide-json /app/examples/slide_color_bg.json

# Результаты появятся в папке output/
```

### Вариант 2: Локальная установка (venv)

```bash
# Клонировать репозиторий
git clone https://github.com/DaniilZebzeev/hse-ml-contrast-checker.git
cd hse-ml-contrast-checker

# Создать виртуальное окружение
python -m venv venv

# Активировать venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### Вариант 3: Локальная сборка Docker

```bash
# Собрать образ
docker build -t hse-contrast-checker .

# Или использовать docker-compose
docker-compose build
```

### Базовое использование CLI

```bash
# Анализ слайда с цветным фоном
python -m src.cli --slide-json examples/slide_color_bg.json

# Анализ с фоновым изображением используя K-means
python -m src.cli \
    --slide-json examples/slide_with_image.json \
    --bg-image examples/background.png \
    --ml-method kmeans

# Пользовательские пути вывода
python -m src.cli \
    --slide-json examples/slide_complex.json \
    --out-json results/my_result.json \
    --out-html results/my_report.html \
    --verbose

# Batch обработка нескольких слайдов
python -m src.batch_analyzer \
    --slides-dir examples/ \
    --output-dir output/ \
    --ml-method kmeans
```

### Запуск веб-интерфейса

```bash
# Запустить Flask веб-приложение
python -m src.webapp

# Приложение будет доступно по адресу http://localhost:5000
# Загружайте HTML презентации или отдельные JSON слайды
# Результаты автоматически сохраняются в web_output/
```

### Использование Docker

```bash
# Используя образ с Docker Hub
docker run -v $(pwd)/output:/app/output \
    danilzebzeev/hse-contrast-checker:latest \
    --slide-json /app/examples/slide_color_bg.json

# Или локально собранный образ
docker run -v $(pwd)/examples:/app/examples -v $(pwd)/output:/app/output \
    hse-contrast-checker --slide-json /app/examples/slide_color_bg.json

# Запуск веб-интерфейса в Docker
docker-compose up webapp

# Используя docker-compose для CLI
docker-compose run contrast-checker \
    --slide-json /app/examples/slide_with_image.json \
    --bg-image /app/examples/background.png
```

## 📚 Как это работает

### 1. Формат входных данных

Инструмент принимает JSON файлы с описанием слайдов:

```json
{
  "id": "slide-001",
  "base_color": "#ffffff",
  "content_html": "<div id=\"text-1\">...</div>"
}
```

### 2. ML извлечение цветов

**Median-cut алгоритм** (по умолчанию):
- Быстрая квантизация палитры
- Рекурсивное деление цветового пространства
- Сложность O(n log n)

**K-means кластеризация**:
- Более точный для сложных изображений
- Подход обучения без учителя
- Находит k центров кластеров в RGB пространстве

### 3. Расчет контрастности WCAG 2.2

Формула: `(L1 + 0.05) / (L2 + 0.05)`

| Уровень | Обычный текст | Крупный текст |
|---------|---------------|---------------|
| AA      | 4.5:1         | 3:1           |
| AAA     | 7:1           | 4.5:1         |

**Крупный текст** = 18pt+ (24px+) ИЛИ 14pt+ жирный (18.67px+ жирный)

### 4. Выходные данные

- **JSON**: Машиночитаемые результаты анализа
- **HTML**: Визуальный отчет с примерами цветов и рекомендациями

## 🏗️ Архитектура

```
┌─────────────────┐
│   CLI (click)   │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │ contrast_checker.py  │ ◄─── Главный оркестратор
    └────┬─────────────────┘
         │
    ┌────▼──────────┬──────────────┬───────────────┐
    │               │              │               │
┌───▼────┐  ┌──────▼─────┐  ┌────▼─────┐  ┌─────▼────┐
│color_  │  │html_       │  │image_    │  │wcag.py   │
│parser  │  │parser      │  │analyzer  │  │          │
│        │  │(BS4)       │  │(ML)      │  │(формулы) │
└────────┘  └────────────┘  └──────────┘  └──────────┘
```

Подробнее см. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 🧪 Тестирование

```bash
# Установить dev зависимости
pip install -r requirements-dev.txt

# Запустить тесты
pytest tests/ -v

# С покрытием
pytest tests/ --cov=src --cov-report=html

# Проверка типов
mypy src

# Линтинг
flake8 src tests
black --check src tests
```

## 📖 Документация API

См. [docs/API.md](docs/API.md) для подробной справки API.

## 🤖 ML подход

Этот проект использует **обучение без учителя** для извлечения цветов:

### Median-cut алгоритм
- **Тип**: Рекурсивная квантизация палитры
- **Сложность**: O(n log k)
- **Плюсы**: Быстрый, детерминированный
- **Минусы**: Менее точен для сложных градиентов

### K-means кластеризация
- **Тип**: Итеративная оптимизация кластеров
- **Сложность**: O(n * k * i), где i = итерации
- **Плюсы**: Более точный, находит "истинные" доминирующие цвета
- **Минусы**: Медленнее, требует больше памяти

См. [docs/ML_APPROACH.md](docs/ML_APPROACH.md) для математических деталей.

## 🔧 Конфигурация

### Опции CLI (src.cli)

```
--slide-json PATH       Входной JSON слайда (обязательно)
--slide-index INT       Индекс слайда, если JSON массив
--bg-image PATH         Файл фонового изображения
--ml-method CHOICE      mediancut|kmeans (по умолчанию: mediancut)
--k-colors INT          Количество цветов для извлечения (по умолчанию: 5)
--out-json PATH         Путь выходного JSON
--out-html PATH         Путь выходного HTML отчета
--verbose               Включить подробное логирование
```

### Опции Batch Analyzer (src.batch_analyzer)

```
--slides-dir PATH       Директория с JSON слайдами (обязательно)
--output-dir PATH       Директория для сохранения результатов
--ml-method CHOICE      mediancut|kmeans (по умолчанию: mediancut)
--k-colors INT          Количество цветов для извлечения (по умолчанию: 5)
--verbose               Включить подробное логирование
```

### Веб-интерфейс (src.webapp)

Веб-приложение поддерживает:
- Загрузку HTML презентаций (автоматическое извлечение слайдов)
- Загрузку отдельных JSON слайдов
- Drag-and-drop интерфейс
- Выбор ML метода (median-cut / K-means)
- Просмотр результатов в браузере
- Скачивание JSON отчетов

Результаты сохраняются в `web_output/<session_id>/`

## 📊 Пример вывода

### Консольный вывод
```
Analysis complete!
  Slide ID: slide-001
  Total entities: 3
  Passed AA Normal: 2
  Failed AA Normal: 1

  JSON: output/result.json
  HTML: output/report.html
```

### HTML отчет
HTML отчет включает:
- Сводку с эффективным цветом фона
- Контрастность для каждого элемента
- Значки соответствия WCAG (AA Normal, AA Large, AAA)
- Визуальные примеры комбинаций текст/фон
- Практические рекомендации для неудачных элементов

## 🛠️ Разработка

### Структура проекта

```
hse-ml-contrast-checker-main/
├── src/
│   ├── cli.py                        # CLI-интерфейс
│   ├── batch_analyzer.py             # Batch обработка слайдов
│   ├── webapp.py                     # Flask веб-приложение
│   ├── slide_scraper.py              # Базовый scraper HTML презентаций
│   ├── slide_scraper_advanced.py     # Продвинутый scraper с поддержкой reveal.js
│   ├── color_parser.py               # Парсинг CSS-цветов
│   ├── color_parser_constants.py
│   ├── contrast_checker.py           # Главный оркестратор
│   ├── html_parser.py                # Извлечение элементов с помощью BeautifulSoup
│   ├── image_analyzer.py             # Анализ изображений и ML-алгоритмы
│   ├── report_generator.py           # Генерация HTML-отчётов
│   ├── wcag.py                       # Расчёты по стандарту WCAG
│   └── wcag_constants.py
├── templates/                        # HTML шаблоны для веб-интерфейса
│   └── index.html
├── static/                           # Статические файлы (CSS, JS)
│   ├── styles.css
│   └── app.js
├── tests/                            # pytest тесты
│   ├── test_color_parser.py
│   ├── test_html_parser.py
│   ├── test_image_analyzer.py
│   ├── test_slide_scraper.py
│   └── test_webapp.py
├── examples/                         # Примеры JSON файлов
├── docs/                             # Документация
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── ML_APPROACH.md
├── Dockerfile                        # Multi-stage Docker build
├── docker-compose.yml                # Конфигурация Docker Compose
├── requirements.txt                  # Production зависимости
└── requirements-dev.txt              # Development зависимости
```

### Стиль кода

- **Форматирование**: Black (длина строки 120)
- **Линтинг**: flake8
- **Проверка типов**: mypy
- **Docstrings**: Google style

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'feat: add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT - см. файл [LICENSE](LICENSE) для деталей.

## 👥 Авторы

- https://github.com/JuliaPonomareva
- https://github.com/VKristin
- https://github.com/DaniilZebzeev

## 🙏 Благодарности

- Руководство WCAG 2.2
- scikit-learn за реализацию K-means
- Pillow за обработку изображений
- BeautifulSoup за парсинг HTML

---

**Создано для курса "Прикладные аспекты машинного обучения" ВШЭ**
