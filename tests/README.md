# Тесты HSE ML Contrast Checker

Набор тестов для проверки функциональности проекта.

## Структура тестов

```
tests/
├── __init__.py              # Инициализация пакета тестов
├── conftest.py              # Общие фикстуры для всех тестов
├── test_webapp.py           # Тесты для FastAPI веб-приложения
├── test_slide_scraper.py    # Тесты для модуля извлечения слайдов
└── README.md                # Этот файл
```

## Установка зависимостей для тестирования

```bash
# Установить все зависимости для разработки
pip install -r requirements-dev.txt
```

## Запуск тестов

### Запустить все тесты

```bash
pytest
```

### Запустить с подробным выводом

```bash
pytest -v
```

### Запустить с покрытием кода

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Запустить конкретный тестовый файл

```bash
pytest tests/test_webapp.py
```

### Запустить конкретный тестовый класс

```bash
pytest tests/test_webapp.py::TestHealthEndpoint
```

### Запустить конкретный тест

```bash
pytest tests/test_webapp.py::TestHealthEndpoint::test_health_check
```

### Запустить тесты по маркерам

```bash
# Только API тесты
pytest -m api

# Только тесты scraper
pytest -m scraper

# Исключить медленные тесты
pytest -m "not slow"
```

## Типы тестов

### Unit тесты
- `test_slide_scraper.py` - Тесты отдельных функций парсинга и извлечения

### Integration тесты
- `test_webapp.py` - Тесты API endpoints с моками внешних зависимостей

## Фикстуры

Общие фикстуры доступны в `conftest.py`:

- `temp_dir` - Временная директория для тестов
- `sample_slide_html` - Пример HTML слайда
- `sample_multi_slide_html` - Пример HTML с несколькими слайдами
- `sample_slide_json` - Пример JSON данных слайда
- `sample_analysis_result` - Пример результата анализа
- `html_file` - Временный HTML файл с тестовым содержимым
- `multi_slide_html_file` - Временный HTML файл с несколькими слайдами

## Покрытие тестами

Текущее покрытие включает:

### ✅ Полностью покрыто
- `src/webapp.py` - FastAPI endpoints
- `src/slide_scraper.py` - Функции извлечения слайдов

### 📊 Частично покрыто
- `src/slide_scraper_advanced.py` - Требует мокирование Selenium

### ⏳ Не покрыто
- `src/contrast_checker.py` - Основная логика анализа
- `src/image_analyzer.py` - ML алгоритмы
- `src/wcag.py` - WCAG расчёты
- `src/report_generator.py` - Генерация HTML отчётов

## Добавление новых тестов

### Пример теста для нового модуля

```python
# tests/test_new_module.py
import pytest
from src.new_module import my_function


class TestMyFunction:
    """Tests for my_function."""

    def test_basic_functionality(self):
        """Test basic usage."""
        result = my_function("input")
        assert result == "expected_output"

    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValueError):
            my_function(None)
```

## Continuous Integration

Тесты автоматически запускаются при:
- Push в main ветку
- Создании Pull Request
- Ручном запуске workflow

## Отладка тестов

### Запустить с остановкой на первой ошибке

```bash
pytest -x
```

### Запустить с выводом print statements

```bash
pytest -s
```

### Запустить с Python debugger

```bash
pytest --pdb
```

### Показать локальные переменные при ошибках

```bash
pytest -l
```

## Best Practices

1. **Один тест - одна проверка**: Каждый тест должен проверять одну конкретную вещь
2. **Используйте фикстуры**: Переиспользуйте код через фикстуры в conftest.py
3. **Мокируйте внешние зависимости**: Используйте pytest-mock для изоляции тестов
4. **Понятные названия**: Имена тестов должны описывать что тестируется
5. **Docstrings**: Добавляйте краткое описание что проверяет тест

## Troubleshooting

### Тесты не находятся

Убедитесь что:
- Файлы называются `test_*.py` или `*_test.py`
- Функции называются `test_*()`
- Классы называются `Test*`

### Import ошибки

```bash
# Установите проект в editable mode
pip install -e .
```

### Конфликты версий

```bash
# Пересоздайте виртуальное окружение
rm -rf venv
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements-dev.txt
```

## Дополнительная информация

- [Pytest документация](https://docs.pytest.org/)
- [FastAPI тестирование](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
