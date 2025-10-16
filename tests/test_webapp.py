"""Tests for FastAPI webapp endpoints."""

import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.webapp import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self):
        """Test health check returns 200 and correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_html(self):
        """Test root endpoint returns HTML page."""
        response = client.get("/")
        assert response.status_code in [200, 404]  # 404 if template not found
        assert response.headers["content-type"].startswith("text/html")


class TestAnalyzeURLEndpoint:
    """Tests for /api/analyze-url endpoint."""

    @patch('src.webapp.scrape_all_slides_from_url')
    @patch('src.webapp.analyze_slide')
    @patch('src.webapp.generate_html_report')
    def test_analyze_url_single_slide_success(
        self,
        mock_generate_report,
        mock_analyze,
        mock_scrape
    ):
        """Test successful analysis of single slide from URL."""
        # Mock scraper to return slide data
        mock_scrape.return_value = [{"id": "slide-001", "base_color": "#ffffff"}]

        # Mock analyzer to return result
        mock_analyze.return_value = {
            "slide_id": "slide-001",
            "summary": {
                "total_entities": 3,
                "passed_AA_normal": 2,
                "failed_AA_normal": 1
            },
            "entities": []
        }

        # Mock report generator
        mock_generate_report.return_value = None

        response = client.post(
            "/api/analyze-url",
            data={
                "url": "https://app.diaclass.ru/share/test",
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_slides"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["summary"]["total_entities"] == 3

    @patch('src.webapp.scrape_all_slides_from_url')
    def test_analyze_url_no_slides_found(self, mock_scrape):
        """Test error when no slides are found."""
        mock_scrape.return_value = []

        response = client.post(
            "/api/analyze-url",
            data={
                "url": "https://app.diaclass.ru/share/test",
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            }
        )

        assert response.status_code == 400
        assert "не удалось извлечь слайды" in response.json()["detail"].lower()

    @patch('src.webapp.scrape_all_slides_from_url')
    @patch('src.webapp.analyze_slide')
    @patch('src.webapp.generate_html_report')
    def test_analyze_url_multiple_slides(
        self,
        mock_generate_report,
        mock_analyze,
        mock_scrape
    ):
        """Test analysis of multiple slides."""
        # Mock scraper to return multiple slides
        mock_scrape.return_value = [
            {"id": "slide-001"},
            {"id": "slide-002"},
            {"id": "slide-003"}
        ]

        # Mock analyzer
        mock_analyze.return_value = {
            "slide_id": "slide-001",
            "summary": {
                "total_entities": 3,
                "passed_AA_normal": 2,
                "failed_AA_normal": 1
            },
            "entities": []
        }

        mock_generate_report.return_value = None

        response = client.post(
            "/api/analyze-url",
            data={
                "url": "https://app.diaclass.ru/share/test",
                "ml_method": "kmeans",
                "slide_mode": "all"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_slides"] == 3


class TestAnalyzeFileEndpoint:
    """Tests for /api/analyze-file endpoint."""

    @patch('src.webapp.scrape_all_slides_from_file')
    @patch('src.webapp.analyze_slide')
    @patch('src.webapp.generate_html_report')
    def test_analyze_file_success(
        self,
        mock_generate_report,
        mock_analyze,
        mock_scrape
    ):
        """Test successful file upload and analysis."""
        mock_scrape.return_value = [{"id": "slide-001"}]

        mock_analyze.return_value = {
            "slide_id": "slide-001",
            "summary": {
                "total_entities": 5,
                "passed_AA_normal": 4,
                "failed_AA_normal": 1
            },
            "entities": []
        }

        mock_generate_report.return_value = None

        # Create fake HTML file
        html_content = b"<html><body><div class='swiper-slide'>Test</div></body></html>"

        response = client.post(
            "/api/analyze-file",
            data={
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            },
            files={"file": ("test.html", html_content, "text/html")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_slides"] == 1

    def test_analyze_file_invalid_extension(self):
        """Test error for non-HTML file."""
        response = client.post(
            "/api/analyze-file",
            data={
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            },
            files={"file": ("test.txt", b"test content", "text/plain")}
        )

        assert response.status_code == 400
        assert "html" in response.json()["detail"].lower()

    @patch('src.webapp.scrape_all_slides_from_file')
    def test_analyze_file_no_slides_found(self, mock_scrape):
        """Test error when file has no slides."""
        mock_scrape.return_value = []

        html_content = b"<html><body>No slides here</body></html>"

        response = client.post(
            "/api/analyze-file",
            data={
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            },
            files={"file": ("test.html", html_content, "text/html")}
        )

        assert response.status_code == 400
        assert "не удалось извлечь слайды" in response.json()["detail"].lower()


class TestMLMethodParameter:
    """Tests for ML method parameter validation."""

    @patch('src.webapp.scrape_all_slides_from_url')
    @patch('src.webapp.analyze_slide')
    @patch('src.webapp.generate_html_report')
    def test_mediancut_method(self, mock_gen, mock_analyze, mock_scrape):
        """Test using median cut method."""
        mock_scrape.return_value = [{"id": "slide-001"}]
        mock_analyze.return_value = {
            "slide_id": "slide-001",
            "summary": {"total_entities": 1, "passed_AA_normal": 1, "failed_AA_normal": 0},
            "entities": []
        }
        mock_gen.return_value = None

        response = client.post(
            "/api/analyze-url",
            data={
                "url": "https://app.diaclass.ru/share/test",
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            }
        )

        assert response.status_code == 200
        # Verify analyze_slide was called with mediancut
        mock_analyze.assert_called()
        call_kwargs = mock_analyze.call_args.kwargs
        assert call_kwargs["ml_method"] == "mediancut"

    @patch('src.webapp.scrape_all_slides_from_url')
    @patch('src.webapp.analyze_slide')
    @patch('src.webapp.generate_html_report')
    def test_kmeans_method(self, mock_gen, mock_analyze, mock_scrape):
        """Test using k-means method."""
        mock_scrape.return_value = [{"id": "slide-001"}]
        mock_analyze.return_value = {
            "slide_id": "slide-001",
            "summary": {"total_entities": 1, "passed_AA_normal": 1, "failed_AA_normal": 0},
            "entities": []
        }
        mock_gen.return_value = None

        response = client.post(
            "/api/analyze-url",
            data={
                "url": "https://app.diaclass.ru/share/test",
                "ml_method": "kmeans",
                "slide_mode": "single",
                "slide_index": 1
            }
        )

        assert response.status_code == 200
        # Verify analyze_slide was called with kmeans
        mock_analyze.assert_called()
        call_kwargs = mock_analyze.call_args.kwargs
        assert call_kwargs["ml_method"] == "kmeans"


class TestErrorHandling:
    """Tests for error handling."""

    @patch('src.webapp.scrape_all_slides_from_url')
    def test_scraper_exception_handled(self, mock_scrape):
        """Test that scraper exceptions are handled properly."""
        mock_scrape.side_effect = Exception("Selenium error")

        response = client.post(
            "/api/analyze-url",
            data={
                "url": "https://app.diaclass.ru/share/test",
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            }
        )

        assert response.status_code == 500
        assert "ошибка" in response.json()["detail"].lower()

    @patch('src.webapp.scrape_all_slides_from_url')
    @patch('src.webapp.analyze_slide')
    def test_analyzer_exception_handled(self, mock_analyze, mock_scrape):
        """Test that analyzer exceptions are handled properly."""
        mock_scrape.return_value = [{"id": "slide-001"}]
        mock_analyze.side_effect = Exception("Analysis failed")

        response = client.post(
            "/api/analyze-url",
            data={
                "url": "https://app.diaclass.ru/share/test",
                "ml_method": "mediancut",
                "slide_mode": "single",
                "slide_index": 1
            }
        )

        assert response.status_code == 500
        assert "ошибка" in response.json()["detail"].lower()
