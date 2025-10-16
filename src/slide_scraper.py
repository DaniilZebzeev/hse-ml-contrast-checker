"""Slide Scraper for extracting slide data from Diaclass HTML."""

import re
import json
import requests
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from pathlib import Path


def fetch_html_from_url(url: str, timeout: int = 10) -> str:
    """
    Fetch HTML content from URL.

    Args:
        url: URL to fetch HTML from
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        requests.RequestException: If request fails
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch HTML from {url}: {e}")


def load_html_from_file(file_path: str) -> str:
    """
    Load HTML content from file.

    Args:
        file_path: Path to HTML file

    Returns:
        HTML content as string
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text(encoding='utf-8')


def extract_background_color(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract background color from slide HTML.

    Looks for .slide__bg-color element with background-color style.

    Args:
        soup: BeautifulSoup object

    Returns:
        Background color as hex string or None
    """
    bg_div = soup.find('div', class_=re.compile(r'slide__bg-color'))
    if not bg_div:
        return None

    style = bg_div.get('style', '')
    if not style:
        return None

    # Extract background-color from style
    # Example: "background-color: rgba(79, 174, 255, 0.15);"
    bg_match = re.search(r'background-color:\s*([^;]+)', style)
    if not bg_match:
        return None

    color_value = bg_match.group(1).strip()

    # Convert rgba to rgb (ignoring alpha)
    rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', color_value)
    if rgba_match:
        r, g, b = rgba_match.groups()
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    return color_value


def extract_text_entities(soup: BeautifulSoup, max_entities: int = 20) -> str:
    """
    Extract text entities from slide HTML and build content_html.

    Args:
        soup: BeautifulSoup object
        max_entities: Maximum number of text entities to extract

    Returns:
        HTML string for content_html field
    """
    entities_html = []
    seen_texts = set()  # Track unique texts

    # Find all swiper-slide divs (multiple slides in presentation)
    slides = soup.find_all('div', class_='swiper-slide', limit=5)

    if not slides:
        # Fallback to single slide
        slides = [soup]

    for slide_elem in slides:
        # Find all text entities in the current slide
        text_divs = slide_elem.find_all('div', attrs={'data-type': 'text'}, limit=max_entities)

        for idx, div in enumerate(text_divs, 1):
            entity_id = div.get('id', f'text-{len(entities_html) + 1}')

            # Extract text and style from spans
            spans = div.find_all('span', style=True)
            if not spans:
                continue

            # Get first span for extracting color and font-size
            first_span = spans[0]
            style_str = first_span.get('style', '')
            text_content = div.get_text(strip=True)

            if not text_content or text_content in seen_texts:
                continue

            seen_texts.add(text_content)

            # Extract color (handle both hsl and hex)
            color_match = re.search(r'color:\s*([^;]+)', style_str)
            color = color_match.group(1).strip() if color_match else '#000000'

            # Extract font-size
            size_match = re.search(r'font-size:\s*(\d+)px', style_str)
            font_size = size_match.group(1) if size_match else '16'

            # Extract font-weight
            weight_match = re.search(r'font-weight:\s*(\d+|bold|normal)', style_str)
            font_weight = ''
            if weight_match:
                weight = weight_match.group(1)
                if weight in ['bold', 'normal'] or (weight.isdigit() and int(weight) >= 700):
                    font_weight = f'; font-weight: {weight}'

            # Build entity HTML
            entity_html = f'<div id="{entity_id}" style="color: {color}; font-size: {font_size}px{font_weight}">{text_content}</div>'
            entities_html.append(entity_html)

            if len(entities_html) >= max_entities:
                break

        if len(entities_html) >= max_entities:
            break

    return ''.join(entities_html)


def parse_slide_html(html_content: str, slide_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse Diaclass slide HTML and extract slide data.

    Args:
        html_content: HTML content string
        slide_id: Optional slide ID (auto-generated if not provided)

    Returns:
        Dictionary with slide data in the format:
        {
            "id": "slide-001",
            "base_color": "#e6f2ff",
            "content_html": "<div>...</div>"
        }
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract background color
    bg_color = extract_background_color(soup)
    if not bg_color:
        bg_color = "#ffffff"  # Default to white

    # Extract text entities
    content_html = extract_text_entities(soup)

    # Generate slide ID if not provided
    if not slide_id:
        slide_id = "extracted-slide-001"

    return {
        "id": slide_id,
        "base_color": bg_color,
        "content_html": content_html
    }


def scrape_slide_from_url(url: str, output_path: Optional[str] = None, slide_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Scrape slide data from URL and optionally save to JSON.

    Args:
        url: URL to fetch HTML from
        output_path: Optional path to save JSON file
        slide_id: Optional slide ID

    Returns:
        Dictionary with slide data
    """
    print(f"Fetching HTML from: {url}")
    html_content = fetch_html_from_url(url)

    print("Parsing slide data...")
    slide_data = parse_slide_html(html_content, slide_id)

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(slide_data, f, indent=2, ensure_ascii=False)

        print(f"Slide data saved to: {output_path}")

    return slide_data


def scrape_slide_from_file(file_path: str, output_path: Optional[str] = None, slide_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Scrape slide data from HTML file and optionally save to JSON.

    Args:
        file_path: Path to HTML file
        output_path: Optional path to save JSON file
        slide_id: Optional slide ID

    Returns:
        Dictionary with slide data
    """
    print(f"Loading HTML from: {file_path}")
    html_content = load_html_from_file(file_path)

    print("Parsing slide data...")
    slide_data = parse_slide_html(html_content, slide_id)

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(slide_data, f, indent=2, ensure_ascii=False)

        print(f"Slide data saved to: {output_path}")

    return slide_data


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.slide_scraper <url_or_file> [output.json]")
        sys.exit(1)

    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        if source.startswith('http'):
            slide_data = scrape_slide_from_url(source, output)
        else:
            slide_data = scrape_slide_from_file(source, output)

        print("\nExtracted slide data:")
        print(json.dumps(slide_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
