"""Tests for slide scraper module."""

import pytest
from pathlib import Path
from bs4 import BeautifulSoup

from src.slide_scraper import (
    extract_background_color,
    extract_text_entities,
    parse_slide_html,
    scrape_slide_from_file
)


class TestExtractBackgroundColor:
    """Tests for background color extraction."""

    def test_extract_rgba_background(self):
        """Test extraction of RGBA background color."""
        html = """
        <div class="slide__bg-color" style="background-color: rgba(79, 174, 255, 0.15);">
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        color = extract_background_color(soup)
        assert color == "#4faeff"

    def test_extract_rgb_background(self):
        """Test extraction of RGB background color."""
        html = """
        <div class="slide__bg-color" style="background-color: rgb(255, 100, 50);">
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        color = extract_background_color(soup)
        assert color == "#ff6432"

    def test_no_background_element(self):
        """Test when no background element exists."""
        html = "<div>No background here</div>"
        soup = BeautifulSoup(html, 'html.parser')
        color = extract_background_color(soup)
        assert color is None

    def test_background_without_style(self):
        """Test background element without style attribute."""
        html = '<div class="slide__bg-color"></div>'
        soup = BeautifulSoup(html, 'html.parser')
        color = extract_background_color(soup)
        assert color is None


class TestExtractTextEntities:
    """Tests for text entity extraction."""

    def test_extract_single_text_entity(self):
        """Test extraction of single text entity."""
        html = """
        <div data-type="text" id="text-1">
            <span style="color: #000000; font-size: 16px;">Hello World</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content_html = extract_text_entities(soup)

        assert "Hello World" in content_html
        assert 'id="text-1"' in content_html
        assert "color: #000000" in content_html
        assert "font-size: 16px" in content_html

    def test_extract_multiple_text_entities(self):
        """Test extraction of multiple text entities."""
        html = """
        <div data-type="text" id="text-1">
            <span style="color: #ff0000; font-size: 20px;">Title</span>
        </div>
        <div data-type="text" id="text-2">
            <span style="color: #0000ff; font-size: 14px;">Body</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content_html = extract_text_entities(soup)

        assert "Title" in content_html
        assert "Body" in content_html
        assert content_html.count("<div") == 2

    def test_extract_with_bold_text(self):
        """Test extraction of bold text."""
        html = """
        <div data-type="text" id="text-1">
            <span style="color: #000000; font-size: 18px; font-weight: bold;">Bold Text</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content_html = extract_text_entities(soup)

        assert "Bold Text" in content_html
        assert "font-weight: bold" in content_html or "font-weight: 700" in content_html

    def test_ignore_duplicate_text(self):
        """Test that duplicate text is ignored."""
        html = """
        <div data-type="text" id="text-1">
            <span style="color: #000000; font-size: 16px;">Same Text</span>
        </div>
        <div data-type="text" id="text-2">
            <span style="color: #000000; font-size: 16px;">Same Text</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content_html = extract_text_entities(soup)

        # Should only appear once
        assert content_html.count("Same Text") == 1

    def test_limit_max_entities(self):
        """Test that max_entities limit is respected."""
        # Create HTML with many entities
        divs = []
        for i in range(30):
            divs.append(f'''
                <div data-type="text" id="text-{i}">
                    <span style="color: #000000; font-size: 16px;">Text {i}</span>
                </div>
            ''')
        html = ''.join(divs)
        soup = BeautifulSoup(html, 'html.parser')

        content_html = extract_text_entities(soup, max_entities=10)

        # Should have at most 10 divs
        assert content_html.count("<div") <= 10


class TestParseSlideHTML:
    """Tests for full slide parsing."""

    def test_parse_complete_slide(self):
        """Test parsing a complete slide with background and text."""
        html = """
        <html>
            <div class="slide__bg-color" style="background-color: rgba(230, 242, 255, 1);">
            </div>
            <div data-type="text" id="text-1">
                <span style="color: #333333; font-size: 24px; font-weight: bold;">Title</span>
            </div>
            <div data-type="text" id="text-2">
                <span style="color: #666666; font-size: 16px;">Content</span>
            </div>
        </html>
        """

        result = parse_slide_html(html, slide_id="test-slide")

        assert result["id"] == "test-slide"
        assert result["base_color"] == "#e6f2ff"
        assert "Title" in result["content_html"]
        assert "Content" in result["content_html"]

    def test_parse_slide_no_background(self):
        """Test parsing slide without background defaults to white."""
        html = """
        <html>
            <div data-type="text" id="text-1">
                <span style="color: #000000; font-size: 16px;">Test</span>
            </div>
        </html>
        """

        result = parse_slide_html(html)

        assert result["base_color"] == "#ffffff"
        assert "Test" in result["content_html"]

    def test_parse_slide_auto_id(self):
        """Test automatic ID generation when not provided."""
        html = "<html><body>Test</body></html>"

        result = parse_slide_html(html)

        assert result["id"] == "extracted-slide-001"

    def test_parse_empty_slide(self):
        """Test parsing slide with no text entities."""
        html = """
        <html>
            <div class="slide__bg-color" style="background-color: rgb(255, 255, 255);"></div>
        </html>
        """

        result = parse_slide_html(html)

        assert result["base_color"] == "#ffffff"
        assert result["content_html"] == ""


class TestScrapeSlideFromFile:
    """Tests for file-based scraping."""

    def test_scrape_from_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            scrape_slide_from_file("/nonexistent/path/file.html")

    def test_scrape_and_save_json(self, tmp_path):
        """Test scraping and saving to JSON file."""
        # Create test HTML file
        html_file = tmp_path / "test_slide.html"
        html_content = """
        <html>
            <div class="slide__bg-color" style="background-color: rgb(100, 150, 200);"></div>
            <div data-type="text" id="text-1">
                <span style="color: #000000; font-size: 16px;">Test Content</span>
            </div>
        </html>
        """
        html_file.write_text(html_content, encoding='utf-8')

        # Output JSON path
        output_json = tmp_path / "output.json"

        # Scrape
        result = scrape_slide_from_file(
            str(html_file),
            output_path=str(output_json),
            slide_id="test-001"
        )

        # Verify result
        assert result["id"] == "test-001"
        assert result["base_color"] == "#6496c8"
        assert "Test Content" in result["content_html"]

        # Verify file was created
        assert output_json.exists()

        # Verify JSON content
        import json
        with open(output_json, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data["id"] == "test-001"


class TestMultipleSlides:
    """Tests for handling multiple slides in one HTML."""

    def test_extract_from_multiple_swiper_slides(self):
        """Test extracting text from multiple swiper slides."""
        html = """
        <html>
            <div class="swiper-slide">
                <div data-type="text">
                    <span style="color: #000000; font-size: 16px;">Slide 1 Text</span>
                </div>
            </div>
            <div class="swiper-slide">
                <div data-type="text">
                    <span style="color: #000000; font-size: 16px;">Slide 2 Text</span>
                </div>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        content_html = extract_text_entities(soup)

        # Should extract from multiple slides
        assert "Slide 1 Text" in content_html
        assert "Slide 2 Text" in content_html
