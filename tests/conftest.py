"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_slide_html():
    """Sample slide HTML for testing."""
    return """
    <html>
        <head><title>Test Slide</title></head>
        <body>
            <div class="slide__bg-color" style="background-color: rgba(230, 242, 255, 1);">
            </div>
            <div data-type="text" id="text-1">
                <span style="color: #333333; font-size: 24px; font-weight: bold;">Test Title</span>
            </div>
            <div data-type="text" id="text-2">
                <span style="color: #666666; font-size: 16px;">Test content goes here</span>
            </div>
            <div data-type="text" id="text-3">
                <span style="color: #999999; font-size: 14px;">Footer text</span>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_multi_slide_html():
    """Sample HTML with multiple slides."""
    return """
    <html>
        <head><title>Multi Slide</title></head>
        <body>
            <div class="swiper-slide">
                <div class="slide__bg-color" style="background-color: rgb(255, 200, 200);"></div>
                <div data-type="text">
                    <span style="color: #000000; font-size: 20px;">Slide 1 Title</span>
                </div>
            </div>
            <div class="swiper-slide">
                <div class="slide__bg-color" style="background-color: rgb(200, 255, 200);"></div>
                <div data-type="text">
                    <span style="color: #000000; font-size: 20px;">Slide 2 Title</span>
                </div>
            </div>
            <div class="swiper-slide">
                <div class="slide__bg-color" style="background-color: rgb(200, 200, 255);"></div>
                <div data-type="text">
                    <span style="color: #000000; font-size: 20px;">Slide 3 Title</span>
                </div>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_slide_json():
    """Sample slide JSON data."""
    return {
        "id": "slide-001",
        "base_color": "#e6f2ff",
        "content_html": """
            <div id="text-1" style="color: #333333; font-size: 24px; font-weight: bold">Test Title</div>
            <div id="text-2" style="color: #666666; font-size: 16px">Test content</div>
        """
    }


@pytest.fixture
def sample_analysis_result():
    """Sample analysis result for testing."""
    return {
        "slide_id": "slide-001",
        "base_color": "#e6f2ff",
        "effective_bg_color": "#e6f2ff",
        "ml_method": "mediancut",
        "entities": [
            {
                "entity_id": "text-1",
                "text_color": "#333333",
                "bg_color": "#e6f2ff",
                "contrast_ratio": 5.2,
                "passes_AA_normal": True,
                "passes_AA_large": True,
                "passes_AAA_normal": False,
                "passes_AAA_large": True
            },
            {
                "entity_id": "text-2",
                "text_color": "#666666",
                "bg_color": "#e6f2ff",
                "contrast_ratio": 3.8,
                "passes_AA_normal": False,
                "passes_AA_large": True,
                "passes_AAA_normal": False,
                "passes_AAA_large": False
            }
        ],
        "summary": {
            "total_entities": 2,
            "passed_AA_normal": 1,
            "failed_AA_normal": 1,
            "passed_AA_large": 2,
            "failed_AA_large": 0,
            "passed_AAA_normal": 0,
            "failed_AAA_normal": 2,
            "passed_AAA_large": 1,
            "failed_AAA_large": 1
        }
    }


@pytest.fixture
def mock_selenium_driver(mocker):
    """Mock Selenium WebDriver for testing."""
    mock_driver = mocker.MagicMock()
    mock_driver.page_source = """
    <html>
        <div class="swiper-slide">
            <div data-type="text">
                <span style="color: #000000; font-size: 16px;">Mocked content</span>
            </div>
        </div>
    </html>
    """
    return mock_driver


@pytest.fixture
def html_file(temp_dir, sample_slide_html):
    """Create a temporary HTML file with sample content."""
    html_path = temp_dir / "test_slide.html"
    html_path.write_text(sample_slide_html, encoding='utf-8')
    return html_path


@pytest.fixture
def multi_slide_html_file(temp_dir, sample_multi_slide_html):
    """Create a temporary HTML file with multiple slides."""
    html_path = temp_dir / "multi_slide.html"
    html_path.write_text(sample_multi_slide_html, encoding='utf-8')
    return html_path
