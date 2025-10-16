# 🌐 HSE ML Contrast Checker - Веб-приложение

Веб-интерфейс для анализа контрастности слайдов с использованием машинного обучения.

## 📋 Возможности

- 🔗 **Анализ по URL**: Загрузка слайдов напрямую из Diaclass через Selenium
- 📁 **Загрузка файлов**: Анализ локальных HTML файлов с презентациями
- 🤖 **Выбор ML метода**: K-means или Median Cut
- 🎯 **Гибкие режимы**: Анализ одного слайда или всей презентации
- 📊 **Визуальные отчёты**: HTML отчёты с результатами анализа WCAG

## 🚀 Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Собрать и запустить
docker-compose up --build

# Веб-приложение будет доступно по адресу:
# http://localhost:8000
```

### Вариант 2: Локальный запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить веб-сервер
uvicorn src.webapp:app --host 0.0.0.0 --port 8000 --reload

# Открыть в браузере:
# http://localhost:8000
```

## 📖 Использование

### Через веб-интерфейс

1. Откройте http://localhost:8000 в браузере
2. Выберите способ загрузки:
   - **По URL**: Вставьте ссылку на презентацию Diaclass
   - **Загрузка файла**: Выберите HTML файл с компьютера
3. Настройте параметры:
   - **Метод ML**: Median Cut (быстрее) или K-means (точнее)
   - **Режим**: Один слайд или вся презентация
   - **Номер слайда**: Если выбран режим "Один слайд"
4. Нажмите "Анализировать"
5. Просмотрите результаты:
   - Статистика по каждому слайду
   - Ссылки на HTML отчёты
   - Скачивание JSON результатов

### Через API

#### Анализ по URL

```bash
curl -X POST "http://localhost:8000/api/analyze-url" \
  -F "url=https://app.diaclass.ru/share/xxx" \
  -F "ml_method=mediancut" \
  -F "slide_mode=single" \
  -F "slide_index=1"
```

#### Анализ файла

```bash
curl -X POST "http://localhost:8000/api/analyze-file" \
  -F "file=@presentation.html" \
  -F "ml_method=kmeans" \
  -F "slide_mode=all"
```

#### Проверка здоровья сервиса

```bash
curl http://localhost:8000/health
```

## 🐳 Docker команды

```bash
# Запустить веб-приложение
docker-compose up

# Запустить в фоне
docker-compose up -d

# Остановить
docker-compose down

# Пересобрать после изменений
docker-compose up --build

# Просмотр логов
docker-compose logs -f web

# Запустить CLI версию (без веб-интерфейса)
docker-compose run --rm cli --slide-json /app/examples/slide_color_bg.json
```

## 📁 Структура проекта

```
.
├── src/
│   ├── webapp.py                  # FastAPI приложение
│   ├── slide_scraper_advanced.py  # Scraper с Selenium
│   ├── contrast_checker.py        # Основная логика анализа
│   └── ...
├── templates/
│   └── index.html                 # Лендинг страница
├── static/
│   ├── styles.css                 # Стили
│   └── app.js                     # JavaScript
├── web_output/                    # Результаты анализа
├── Dockerfile                     # Docker образ с Chrome
├── docker-compose.yml             # Docker Compose конфиг
└── requirements.txt               # Python зависимости
```

## 🔧 Конфигурация

### Переменные окружения

- `PYTHONUNBUFFERED=1` - Отключение буферизации Python
- `DISPLAY=:99` - Виртуальный дисплей для Chrome

### Порты

- `8000` - Веб-приложение FastAPI

### Volumes

- `./web_output:/app/web_output` - Результаты анализа
- `./examples:/app/examples:ro` - Примеры (только чтение)

## 🛠️ Разработка

### Локальная разработка

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить с автоперезагрузкой
uvicorn src.webapp:app --reload --host 0.0.0.0 --port 8000

# Открыть документацию API
# http://localhost:8000/docs
```

### Swagger UI

FastAPI автоматически генерирует интерактивную документацию API:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Главная страница (лендинг) |
| GET | `/health` | Проверка здоровья сервиса |
| POST | `/api/analyze-url` | Анализ слайдов по URL |
| POST | `/api/analyze-file` | Анализ загруженного файла |
| GET | `/results/{session_id}/{filename}` | Получить файл результата |

## 🐛 Решение проблем

### Chrome не запускается в Docker

Убедитесь, что в docker-compose.yml установлена переменная `DISPLAY=:99`

### Selenium ошибки

Проверьте, что ChromeDriver совместим с установленной версией Chrome:

```bash
# Внутри контейнера
google-chrome --version
chromedriver --version
```

### Порт 8000 занят

Измените порт в docker-compose.yml:

```yaml
ports:
  - "8080:8000"  # Вместо 8000:8000
```

## 🎯 Примеры использования

### Анализ одного слайда по URL

1. Откройте http://localhost:8000
2. Выберите вкладку "Загрузить по URL"
3. Вставьте URL презентации
4. Выберите "Median Cut" и "Один слайд"
5. Укажите номер слайда (например, 1)
6. Нажмите "Анализировать"

### Анализ всей презентации из файла

1. Откройте http://localhost:8000
2. Выберите вкладку "Загрузить HTML файл"
3. Загрузите HTML файл с презентацией
4. Выберите "K-means" и "Вся презентация"
5. Нажмите "Анализировать"

## 📝 Лицензия

MIT License - см. файл LICENSE

## 👥 Авторы

- https://github.com/JuliaPonomareva
- https://github.com/VKristin
- https://github.com/DaniilZebzeev

---

**Создано для курса "Прикладные аспекты машинного обучения" ВШЭ**
