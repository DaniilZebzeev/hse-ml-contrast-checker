# Multi-stage Docker build for HSE ML Contrast Checker Web App

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies to user directory
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime with Chrome for Selenium
FROM python:3.11-slim

WORKDIR /app

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN wget -q https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE -O /tmp/version \
    && CHROMEDRIVER_VERSION=$(cat /tmp/version) \
    && wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver* /tmp/version

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy source code, examples, static files, and templates
COPY src/ ./src/
COPY examples/ ./examples/
COPY static/ ./static/
COPY templates/ ./templates/

# Create output directory
RUN mkdir -p web_output

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI web server
CMD ["uvicorn", "src.webapp:app", "--host", "0.0.0.0", "--port", "8000"]
