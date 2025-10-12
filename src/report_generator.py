"""Report Generator for contrast analysis results.

Supports JSON (default) and HTML output formats.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


def generate_report(
    result: Dict[str, Any],
    output_path: str,
    format: str = "json",
    pretty: bool = True
) -> None:
    """
    Generate analysis report in specified format.

    Args:
        result: Analysis result dictionary from analyze_slide()
        output_path: Path to save report
        format: Output format - 'json' (default) or 'html'
        pretty: For JSON: pretty-print with indentation (default True)

    Raises:
        ValueError: If format is not supported
        IOError: If file cannot be written
    """
    if not isinstance(result, dict):
        raise ValueError("Result must be a dictionary")

    format = format.lower().strip()

    if format == "json":
        generate_json_report(result, output_path, pretty=pretty)
    elif format == "html":
        generate_html_report(result, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json' or 'html'")


def generate_json_report(
    result: Dict[str, Any],
    output_path: str,
    pretty: bool = True
) -> None:
    """
    Generate JSON report with standardized structure.

    Args:
        result: Analysis result dictionary from analyze_slide()
        output_path: Path to save JSON report
        pretty: Pretty-print with indentation (default True)
    """
    try:
        # Standardize output structure
        standardized = _standardize_result(result)

        # Create parent directories if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON
        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(standardized, f, indent=2, ensure_ascii=False)
            else:
                json.dump(standardized, f, ensure_ascii=False)

    except (IOError, OSError) as e:
        raise IOError(f"Failed to write JSON report: {e}")
    except Exception as e:
        raise RuntimeError(f"Error generating JSON report: {e}")


def generate_html_report(result: Dict[str, Any], output_path: str) -> None:
    """
    Generate HTML report with visual examples and WCAG status badges.

    Args:
        result: Analysis result dictionary from analyze_slide()
        output_path: Path to save HTML report
    """
    try:
        # Validate and extract data safely
        slide_id = _safe_get(result, "slide_id", "unknown")
        bg_source = _safe_get(result, "background.source", "unknown")
        bg_rgb = _safe_get(result, "background.effective_rgb", (128, 128, 128))
        ml_method = _safe_get(result, "ml_method", "unknown")
        
        summary = result.get("summary", {})
        total_entities = summary.get("total_entities", 0)
        passed_aa = summary.get("passed_AA_normal", 0)
        failed_aa = summary.get("failed_AA_normal", 0)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contrast Analysis Report - Slide {slide_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .entity-card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .status-pass {{ color: #28a745; font-weight: bold; }}
        .status-fail {{ color: #dc3545; font-weight: bold; }}
        .preview-box {{ display: inline-block; padding: 20px 40px; margin: 10px; border-radius: 4px; font-size: 18px; }}
        .wcag-badges {{ display: flex; gap: 10px; margin: 10px 0; flex-wrap: wrap; }}
        .badge {{ padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .badge-pass {{ background: #28a745; color: white; }}
        .badge-fail {{ background: #dc3545; color: white; }}
        .suggestions {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-top: 15px; border-radius: 4px; }}
        .suggestion-item {{ margin: 8px 0; padding: 8px; background: white; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
    </style>
</head>
<body>
    <h1>Contrast Analysis Report</h1>

    <div class="summary">
        <h2>Slide #{slide_id}</h2>
        <p><strong>Background:</strong> {bg_source}</p>
        <p><strong>Effective Background RGB:</strong>
            <span style="display: inline-block; width: 24px; height: 24px; background: rgb{bg_rgb}; border: 1px solid #ccc; vertical-align: middle; margin-right: 8px;"></span>
            rgb{bg_rgb}
        </p>
        <p><strong>ML Method:</strong> {ml_method}</p>
        <p><strong>Total Entities:</strong> {total_entities}</p>
        <p><strong>Passed AA Normal:</strong> <span class="status-pass">{passed_aa}</span></p>
        <p><strong>Failed AA Normal:</strong> <span class="status-fail">{failed_aa}</span></p>
    </div>
"""

        entities = result.get("entities", [])
        for ent in entities:
            html += _generate_entity_card_html(ent, bg_rgb)

        html += """
</body>
</html>
"""

        # Create parent directories if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    except (IOError, OSError) as e:
        raise IOError(f"Failed to write HTML report: {e}")
    except Exception as e:
        raise RuntimeError(f"Error generating HTML report: {e}")


def _standardize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize result structure for consistent output.

    Args:
        result: Raw analysis result

    Returns:
        Standardized result dictionary
    """
    standardized = {
        "version": "1.0",
        "slide_id": result.get("slide_id", "unknown"),
        "background": {
            "source": result.get("background", {}).get("source", "unknown"),
            "effective_rgb": result.get("background", {}).get("effective_rgb", [128, 128, 128]),
            "colors_analyzed": result.get("background", {}).get("colors_analyzed", [])
        },
        "ml_method": result.get("ml_method", "unknown"),
        "summary": {
            "total_entities": result.get("summary", {}).get("total_entities", 0),
            "passed_AA_normal": result.get("summary", {}).get("passed_AA_normal", 0),
            "failed_AA_normal": result.get("summary", {}).get("failed_AA_normal", 0),
            "passed_AA_large": result.get("summary", {}).get("passed_AA_large", 0),
            "failed_AA_large": result.get("summary", {}).get("failed_AA_large", 0),
            "passed_AAA": result.get("summary", {}).get("passed_AAA", 0),
            "failed_AAA": result.get("summary", {}).get("failed_AAA", 0)
        },
        "entities": []
    }

    # Standardize entities
    for ent in result.get("entities", []):
        standardized_entity = {
            "id": ent.get("id", "unknown"),
            "text_content": ent.get("text_content", ""),
            "font": {
                "size_px": ent.get("font", {}).get("size_px", 16.0),
                "weight": ent.get("font", {}).get("weight", "normal"),
                "is_large": ent.get("font", {}).get("is_large", False)
            },
            "text_colors": ent.get("text_colors", []),
            "contrast": {
                "min_ratio": ent.get("contrast", {}).get("min_ratio", 0.0),
                "max_ratio": ent.get("contrast", {}).get("max_ratio", 0.0),
                "wcag": {
                    "AA_normal": ent.get("contrast", {}).get("wcag", {}).get("AA_normal", False),
                    "AA_large": ent.get("contrast", {}).get("wcag", {}).get("AA_large", False),
                    "AAA": ent.get("contrast", {}).get("wcag", {}).get("AAA", False)
                }
            },
            "suggestions": ent.get("suggestions", [])
        }
        standardized["entities"].append(standardized_entity)

    return standardized


def _generate_entity_card_html(ent: Dict[str, Any], bg_rgb: tuple) -> str:
    """
    Generate HTML for a single entity card.

    Args:
        ent: Entity data dictionary
        bg_rgb: Background RGB tuple

    Returns:
        HTML string for entity card
    """
    try:
        ent_id = ent.get("id", "unknown")
        wcag = ent.get("contrast", {}).get("wcag", {})
        status = "PASS" if wcag.get("AA_normal") else "FAIL"
        status_class = "status-pass" if wcag.get("AA_normal") else "status-fail"

        contrast = ent.get("contrast", {})
        font = ent.get("font", {})

        html = f"""
    <div class="entity-card">
        <h3>{ent_id} <span class="{status_class}">{status}</span></h3>

        <table>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Contrast Ratio (min)</td>
                <td><strong>{contrast.get('min_ratio', 0.0)}:1</strong></td>
            </tr>
            <tr>
                <td>Contrast Ratio (max)</td>
                <td><strong>{contrast.get('max_ratio', 0.0)}:1</strong></td>
            </tr>
            <tr>
                <td>Font Size</td>
                <td>{font.get('size_px', 16.0)}px</td>
            </tr>
            <tr>
                <td>Font Weight</td>
                <td>{font.get('weight', 'normal')}</td>
            </tr>
            <tr>
                <td>Is Large Text</td>
                <td>{'Yes' if font.get('is_large', False) else 'No'}</td>
            </tr>
        </table>

        <div class="wcag-badges">
            <span class="badge badge-{'pass' if wcag.get('AA_normal') else 'fail'}">
                AA Normal: {'✓' if wcag.get('AA_normal') else '✗'}
            </span>
            <span class="badge badge-{'pass' if wcag.get('AA_large') else 'fail'}">
                AA Large: {'✓' if wcag.get('AA_large') else '✗'}
            </span>
            <span class="badge badge-{'pass' if wcag.get('AAA') else 'fail'}">
                AAA: {'✓' if wcag.get('AAA') else '✗'}
            </span>
        </div>

        <h4>Visual Previews:</h4>
        <div>
"""

        for tc in ent.get("text_colors", []):
            tc_css = tc.get("css", "#000000")
            html += f"""
            <div class="preview-box" style="background: rgb{bg_rgb}; color: {tc_css}; font-size: {font.get('size_px', 16)}px; font-weight: {font.get('weight', 'normal')};">
                Sample Text ({tc_css})
            </div>
"""

        html += """
        </div>
"""

        # Add suggestions if failed
        if not wcag.get("AA_normal") and ent.get("suggestions"):
            html += """
        <div class="suggestions">
            <h4>Recommendations:</h4>
"""
            for sug in ent.get("suggestions", []):
                expected_ratio_text = (
                    f"(Expected ratio: {sug.get('expected_ratio')}:1)" if sug.get("expected_ratio") else ""
                )
                html += f"""
            <div class="suggestion-item">
                <strong>{sug.get('type', 'Unknown')}:</strong> {sug.get('description', '')}<br>
                → <code>{sug.get('new_value', '')}</code> {expected_ratio_text}
            </div>
"""
            html += """
        </div>
"""

        html += """
    </div>
"""

        return html

    except Exception:
        # Return minimal card on error
        return f"""
    <div class="entity-card">
        <h3>{ent.get('id', 'unknown')} <span class="status-fail">ERROR</span></h3>
        <p>Error rendering entity card</p>
    </div>
"""


def _safe_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value using dot notation.

    Args:
        data: Dictionary to query
        path: Dot-separated path (e.g., "background.source")
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    try:
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default
    except Exception:
        return default