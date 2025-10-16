# 🎨 HSE ML Contrast Checker

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker Image](https://img.shields.io/docker/v/danilzebzeev/hse-contrast-checker?label=docker&logo=docker)](https://hub.docker.com/r/danilzebzeev/hse-contrast-checker)

Production-ready Python инструмент для анализа контрастности текста и фона согласно стандарту **WCAG 2.2** с использованием **машинного обучения**.

> 🆕 **Новое в версии 1.1:**
> - 🌐 Современный FastAPI веб-интерфейс с интуитивным UI
> - 🔍 Автоматическое извлечение слайдов из HTML презентаций (Selenium поддержка)
> - 📦 Batch анализ всей презентации одной командой
> - 🎯 Выбор режима: анализ одного слайда или всей презентации
> - 📊 Улучшенные HTML отчёты с детальной статистикой
> - 🧪 Расширенное тестовое покрытие

## 📋 Обзор

Этот инструмент анализирует контрастность между текстом и фоном в презентационных слайдах, используя ML алгоритмы для извлечения доминирующих цветов и расчета соответствия WCAG.

### ✨ Ключевые возможности

- ✅ **Соответствие WCAG 2.2**: Точный расчет контрастности по стандарту WCAG
- 🤖 **ML-алгоритмы**: Два алгоритма обучения без учителя для извлечения цветов:
  - **Median-cut** (быстрее, Pillow ADAPTIVE)
  - **K-means кластеризация** (точнее, scikit-learn)
- 🌐 **Современный веб-интерфейс**: FastAPI веб-приложение с интуитивным UI
  - Анализ по URL (с поддержкой Selenium для динамических сайтов)
  - Загрузка HTML файлов презентаций
  - Выбор режима: один слайд или вся презентация
  - Автоматическое извлечение и анализ всех слайдов
- 📦 **Batch обработка**: Анализ множества слайдов одной командой
- 🔍 **Продвинутый scraper**: 
  - Базовый scraper для статических HTML
  - Продвинутый scraper с Selenium для JavaScript-презентаций
  - Поддержка извлечения отдельных слайдов по индексу
  - Автоматическое извлечение всех слайдов из презентации
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
python -m src.batch_analyzer examples/ --output-dir output/batch

# Извлечение слайдов из HTML презентации
# Базовый scraper (для статических HTML)
python -m src.slide_scraper examples/diagclass.html examples/extracted_slide.json

# Продвинутый scraper с Selenium (для динамических презентаций)
# Извлечь все слайды
python -m src.slide_scraper_advanced examples/diagclass.html examples/slides

# Извлечь конкретный слайд (например, слайд 5)
python -m src.slide_scraper_advanced examples/diagclass.html examples/slides --slide-index 5

# Извлечь из URL с использованием Selenium
python -m src.slide_scraper_advanced https://app.diaclass.ru/share/xxx examples/slides
```

### Запуск веб-интерфейса

```bash
# Запустить FastAPI веб-приложение
python -m src.webapp

# Или с uvicorn напрямую
uvicorn src.webapp:app --host 0.0.0.0 --port 8000

# Приложение будет доступно по адресу http://localhost:8000
```

**Возможности веб-интерфейса:**
- 📥 **Загрузка по URL**: Введите URL презентации Diaclass (используется Selenium)
- 📁 **Загрузка HTML файла**: Выберите локальный HTML файл с презентацией
- 🎯 **Режим анализа**: 
  - **Один слайд** - анализ конкретного слайда по индексу
  - **Вся презентация** - автоматический анализ всех слайдов
- ⚙️ **Выбор ML метода**: Median Cut (быстрее) или K-means (точнее)
- 📊 **Результаты**: Просмотр HTML отчетов и скачивание JSON результатов
- 💾 **Автоматическое сохранение**: Все результаты в `web_output/<session_id>/`

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
# Веб-интерфейс будет доступен по адресу http://localhost:8000

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
  "content_html": "<div id=\"text-1\" style=\"color: #333; font-size: 16px\">Текст</div>"
}
```

**Автоматическое извлечение слайдов:**
- Используйте `slide_scraper.py` для простых статических HTML
- Используйте `slide_scraper_advanced.py` для динамических презентаций (с Selenium)
- Извлеките один слайд или всю презентацию целиком

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
slides_dir              Директория с JSON слайдами (обязательно)
--output-dir PATH       Директория для сохранения результатов
--ml-method CHOICE      mediancut|kmeans (по умолчанию: mediancut)
--docker                Использовать Docker для анализа
--docker-image NAME     Имя Docker образа (по умолчанию: hse-contrast-checker)
```

### Опции Slide Scraper (src.slide_scraper_advanced)

```
source                  HTML файл или URL (обязательно)
output_dir              Директория для сохранения JSON (по умолчанию: examples/slides)
--slide-index N         Извлечь только конкретный слайд (1-based индекс)
--wait-time SEC         Время ожидания для Selenium (по умолчанию: 5 сек)
```

### Веб-интерфейс (src.webapp)

Веб-приложение на FastAPI поддерживает:
- **Загрузку по URL**: Автоматическое извлечение с помощью Selenium
- **Загрузку HTML файлов**: Drag-and-drop интерфейс
- **Режимы анализа**:
  - Один слайд (с указанием индекса)
  - Вся презентация (автоматически)
- **Выбор ML метода**: median-cut или K-means
- **Результаты**:
  - Интерактивные HTML отчеты
  - JSON файлы с подробными данными
  - Сводная статистика по всем слайдам

Результаты сохраняются в `web_output/<session_id>/`

**API endpoints:**
- `GET /` - Главная страница веб-интерфейса
- `GET /health` - Проверка состояния сервиса
- `POST /api/analyze-url` - Анализ по URL
- `POST /api/analyze-file` - Анализ загруженного файла
- `GET /api/result/{session_id}/{filename}` - Получение результатов

## 📊 Пример вывода

### Веб-интерфейс
1. Откройте http://localhost:8000
2. Выберите вкладку "Загрузить по URL" или "Загрузить HTML файл"
3. Укажите параметры:
   - ML метод (Median Cut или K-means)
   - Режим (один слайд или вся презентация)
   - Индекс слайда (если выбран режим "один слайд")
4. Нажмите "Анализировать"
5. Просмотрите результаты:
   - Общая статистика по всем слайдам
   - Детальные данные для каждого слайда
   - Ссылки на HTML отчёты и JSON файлы

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

### Batch анализ вывод
```
[1/10] Analyzing slide_001.json...
  [OK] Success!
    Total entities: 5
    Passed AA: 4
    Failed AA: 1

[2/10] Analyzing slide_002.json...
  [OK] Success!
    Total entities: 3
    Passed AA: 3
    Failed AA: 0

...

BATCH ANALYSIS COMPLETE
Total slides: 10
Successful: 10
Failed: 0

Results saved to: output/batch/
Summary: output/batch/batch_summary.json
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
│   ├── webapp.py                     # FastAPI веб-приложение
│   ├── slide_scraper.py              # Базовый scraper для статических HTML
│   ├── slide_scraper_advanced.py     # Продвинутый scraper с Selenium
│   ├── color_parser.py               # Парсинг CSS-цветов (hex, rgb, hsl, named)
│   ├── color_parser_constants.py     # Константы цветов CSS
│   ├── contrast_checker.py           # Главный оркестратор анализа
│   ├── html_parser.py                # Извлечение элементов с BeautifulSoup
│   ├── image_analyzer.py             # ML-алгоритмы извлечения цветов
│   ├── report_generator.py           # Генерация HTML-отчётов
│   ├── wcag.py                       # Расчёты по стандарту WCAG 2.2
│   └── wcag_constants.py             # WCAG константы и пороги
├── templates/                        # HTML шаблоны для веб-интерфейса
│   └── index.html                    # Главная страница веб-приложения
├── static/                           # Статические файлы (CSS, JS)
│   ├── styles.css                    # Стили для веб-интерфейса
│   └── app.js                        # JavaScript логика
├── tests/                            # pytest тесты
│   ├── conftest.py                   # Общие фикстуры
│   ├── test_color_parser.py          # Тесты парсинга цветов
│   ├── test_html_parser.py           # Тесты HTML парсинга
│   ├── test_image_analyzer.py        # Тесты ML алгоритмов
│   ├── test_slide_scraper.py         # Тесты scraper модулей
│   ├── test_webapp.py                # Тесты FastAPI endpoints
│   └── README.md                     # Документация по тестам
├── examples/                         # Примеры JSON и HTML файлов
│   ├── demo_slide.json               # Простой пример слайда
│   ├── slide_color_bg.json           # Слайд с цветным фоном
│   ├── slide_with_image.json         # Слайд с фоновым изображением
│   ├── slide_complex.json            # Сложный слайд
│   └── diagclass.html                # Пример HTML презентации
├── docs/                             # Документация
│   ├── API.md                        # API справка
│   ├── ARCHITECTURE.md               # Описание архитектуры
│   └── ML_APPROACH.md                # ML подход и алгоритмы
├── web_output/                       # Результаты веб-анализа
├── output/                           # Результаты CLI анализа
├── Dockerfile                        # Multi-stage Docker build
├── docker-compose.yml                # Конфигурация Docker Compose
├── pytest.ini                        # Конфигурация pytest
├── requirements.txt                  # Production зависимости
├── requirements-dev.txt              # Development зависимости
├── TESTING_REPORT.md                 # Отчёт о тестировании
└── WEB_APP_README.md                 # Документация веб-приложения
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

- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/) за стандарты доступности
- [scikit-learn](https://scikit-learn.org/) за реализацию K-means
- [Pillow](https://pillow.readthedocs.io/) за обработку изображений
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) за парсинг HTML
- [FastAPI](https://fastapi.tiangolo.com/) за современный веб-фреймворк
- [Selenium](https://www.selenium.dev/) за автоматизацию браузера
- [Click](https://click.palletsprojects.com/) за CLI интерфейс

## 📚 Дополнительная документация

- 📘 [WEB_APP_README.md](WEB_APP_README.md) - Подробная документация веб-приложения
- 📗 [TESTING_REPORT.md](TESTING_REPORT.md) - Отчёт о тестировании
- 📙 [tests/README.md](tests/README.md) - Руководство по запуску тестов
- 📕 [docs/API.md](docs/API.md) - API справка
- 📔 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Описание архитектуры
- 📓 [docs/ML_APPROACH.md](docs/ML_APPROACH.md) - Детали ML алгоритмов

---

**Создано для курса "Прикладные аспекты машинного обучения" ВШЭ**
