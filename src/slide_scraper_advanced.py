"""Advanced Slide Scraper with Selenium and multi-slide support."""

import re
import json
import time
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def fetch_html_with_selenium(url: str, wait_time: int = 5, headless: bool = True) -> str:
    """
    Fetch HTML content from URL using Selenium (handles JavaScript).

    Args:
        url: URL to fetch HTML from
        wait_time: Time to wait for page load in seconds
        headless: Run browser in headless mode

    Returns:
        HTML content as string

    Raises:
        ImportError: If selenium is not installed
        Exception: If browser fails to load page
    """
    if not SELENIUM_AVAILABLE:
        raise ImportError(
            "Selenium is not installed. Install it with: pip install selenium\n"
            "You also need to install Chrome/ChromeDriver or use Firefox with geckodriver."
        )

    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = None
    try:
        print(f"Starting browser...")
        driver = webdriver.Chrome(options=options)

        print(f"Loading page: {url}")
        driver.get(url)

        # Wait for slides to load
        print(f"Waiting {wait_time} seconds for content to load...")
        time.sleep(wait_time)

        # Try to wait for specific element
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "swiper-slide"))
            )
        except:
            print("Warning: Could not find swiper-slide elements, continuing anyway...")

        html_content = driver.page_source
        print(f"HTML loaded: {len(html_content)} characters")

        return html_content

    except Exception as e:
        raise Exception(f"Failed to fetch HTML with Selenium: {e}")
    finally:
        if driver:
            driver.quit()


def extract_individual_slides(html_content: str) -> List[BeautifulSoup]:
    """
    Extract individual slides from presentation HTML.

    Args:
        html_content: Full HTML content

    Returns:
        List of BeautifulSoup objects, one per slide
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all swiper-slide elements
    slide_elements = soup.find_all('div', class_='swiper-slide')

    if not slide_elements:
        print("Warning: No swiper-slide elements found, treating as single slide")
        return [soup]

    print(f"Found {len(slide_elements)} slides in presentation")

    # Convert each slide to BeautifulSoup object
    slide_soups = []
    for slide_elem in slide_elements:
        slide_html = str(slide_elem)
        slide_soup = BeautifulSoup(slide_html, 'html.parser')
        slide_soups.append(slide_soup)

    return slide_soups


def extract_slide_background(slide_soup: BeautifulSoup) -> Optional[str]:
    """Extract background color from a single slide."""
    bg_div = slide_soup.find('div', class_=re.compile(r'slide__bg-color'))
    if not bg_div:
        return None

    style = bg_div.get('style', '')
    if not style:
        return None

    bg_match = re.search(r'background-color:\s*([^;]+)', style)
    if not bg_match:
        return None

    color_value = bg_match.group(1).strip()

    # Convert rgba to hex
    rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', color_value)
    if rgba_match:
        r, g, b = rgba_match.groups()
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    return color_value


def extract_slide_text_entities(slide_soup: BeautifulSoup) -> str:
    """Extract text entities from a single slide."""
    entities_html = []

    # Find all text entities in this slide
    text_divs = slide_soup.find_all('div', attrs={'data-type': 'text'})

    for idx, div in enumerate(text_divs, 1):
        entity_id = div.get('id', f'text-{idx}')

        # Extract text and style from spans
        spans = div.find_all('span', style=True)
        if not spans:
            continue

        first_span = spans[0]
        style_str = first_span.get('style', '')
        text_content = div.get_text(strip=True)

        if not text_content:
            continue

        # Extract color
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

        entity_html = f'<div id="{entity_id}" style="color: {color}; font-size: {font_size}px{font_weight}">{text_content}</div>'
        entities_html.append(entity_html)

    return ''.join(entities_html)


def parse_single_slide(slide_soup: BeautifulSoup, slide_index: int) -> Dict[str, Any]:
    """
    Parse a single slide and return its data.

    Args:
        slide_soup: BeautifulSoup object for the slide
        slide_index: Index of the slide (1-based)

    Returns:
        Dictionary with slide data
    """
    bg_color = extract_slide_background(slide_soup)
    if not bg_color:
        bg_color = "#ffffff"

    content_html = extract_slide_text_entities(slide_soup)

    return {
        "id": f"slide-{slide_index:03d}",
        "base_color": bg_color,
        "content_html": content_html
    }


def scrape_all_slides_from_url(
    url: str,
    output_dir: str = "examples/slides",
    use_selenium: bool = True,
    wait_time: int = 5,
    slide_index: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Scrape slides from URL and save as JSON.

    Args:
        url: URL to fetch presentation from
        output_dir: Directory to save JSON files
        use_selenium: Use Selenium for JavaScript rendering
        wait_time: Time to wait for page load (only for Selenium)
        slide_index: Optional slide index (1-based). If specified, only extracts that slide.

    Returns:
        List of slide data dictionaries
    """
    # Fetch HTML
    if use_selenium:
        print("Using Selenium to fetch HTML...")
        html_content = fetch_html_with_selenium(url, wait_time=wait_time)
    else:
        import requests
        print("Using requests to fetch HTML (may not work for JS sites)...")
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

    # Extract individual slides
    slide_soups = extract_individual_slides(html_content)

    # Filter by slide_index if specified
    if slide_index is not None:
        if slide_index < 1 or slide_index > len(slide_soups):
            raise ValueError(f"Slide index {slide_index} out of range (1-{len(slide_soups)})")

        print(f"Extracting only slide {slide_index} of {len(slide_soups)}")
        slide_soups = [slide_soups[slide_index - 1]]  # Convert to 0-based index
        start_index = slide_index
    else:
        start_index = 1

    # Parse each slide
    all_slides = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for offset, slide_soup in enumerate(slide_soups):
        idx = start_index + offset
        print(f"\nParsing slide {idx}...")
        slide_data = parse_single_slide(slide_soup, idx)

        # Save to file
        slide_file = output_path / f"slide_{idx:03d}.json"
        with open(slide_file, 'w', encoding='utf-8') as f:
            json.dump(slide_data, f, indent=2, ensure_ascii=False)

        print(f"  Saved to: {slide_file}")
        print(f"  Background: {slide_data['base_color']}")
        print(f"  Text entities: {len(slide_data['content_html']) // 100}+ chars")

        all_slides.append(slide_data)

    print(f"\n[OK] Extracted {len(all_slides)} slides to {output_dir}/")

    return all_slides


def scrape_all_slides_from_file(
    file_path: str,
    output_dir: str = "examples/slides",
    slide_index: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Scrape slides from HTML file and save as JSON.

    Args:
        file_path: Path to HTML file
        output_dir: Directory to save JSON files
        slide_index: Optional slide index (1-based). If specified, only extracts that slide.

    Returns:
        List of slide data dictionaries
    """
    print(f"Loading HTML from: {file_path}")

    html_path = Path(file_path)
    if not html_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    html_content = html_path.read_text(encoding='utf-8')

    # Extract individual slides
    slide_soups = extract_individual_slides(html_content)

    # Filter by slide_index if specified
    if slide_index is not None:
        if slide_index < 1 or slide_index > len(slide_soups):
            raise ValueError(f"Slide index {slide_index} out of range (1-{len(slide_soups)})")

        print(f"Extracting only slide {slide_index} of {len(slide_soups)}")
        slide_soups = [slide_soups[slide_index - 1]]  # Convert to 0-based index
        start_index = slide_index
    else:
        start_index = 1

    # Parse each slide
    all_slides = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for offset, slide_soup in enumerate(slide_soups):
        idx = start_index + offset
        print(f"\nParsing slide {idx}...")
        slide_data = parse_single_slide(slide_soup, idx)

        # Save to file
        slide_file = output_path / f"slide_{idx:03d}.json"
        with open(slide_file, 'w', encoding='utf-8') as f:
            json.dump(slide_data, f, indent=2, ensure_ascii=False)

        print(f"  Saved to: {slide_file}")
        print(f"  Background: {slide_data['base_color']}")
        print(f"  Text entities: {len(slide_data['content_html']) // 100}+ chars")

        all_slides.append(slide_data)

    print(f"\n[OK] Extracted {len(all_slides)} slides to {output_dir}/")

    return all_slides


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract slides from Diaclass presentation HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all slides
  python -m src.slide_scraper_advanced examples/diagclass.html

  # Extract only slide 5
  python -m src.slide_scraper_advanced examples/diagclass.html --slide-index 5

  # Extract all slides to custom directory
  python -m src.slide_scraper_advanced examples/diagclass.html examples/my_slides

  # Extract from URL with Selenium
  python -m src.slide_scraper_advanced https://app.diaclass.ru/share/xxx
        """
    )

    parser.add_argument('source', help='HTML file path or URL')
    parser.add_argument('output_dir', nargs='?', default='examples/slides',
                       help='Output directory (default: examples/slides)')
    parser.add_argument('--slide-index', type=int, metavar='N',
                       help='Extract only specific slide (1-based index)')
    parser.add_argument('--wait-time', type=int, default=5,
                       help='Selenium wait time in seconds (default: 5)')

    args = parser.parse_args()

    try:
        if args.source.startswith('http'):
            slides = scrape_all_slides_from_url(
                args.source,
                args.output_dir,
                use_selenium=True,
                wait_time=args.wait_time,
                slide_index=args.slide_index
            )
        else:
            slides = scrape_all_slides_from_file(
                args.source,
                args.output_dir,
                slide_index=args.slide_index
            )

        print(f"\n{'='*60}")
        if args.slide_index:
            print(f"SUMMARY: Extracted slide {args.slide_index} successfully!")
        else:
            print(f"SUMMARY: Extracted {len(slides)} slides successfully!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
