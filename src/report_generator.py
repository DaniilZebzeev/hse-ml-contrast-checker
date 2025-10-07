"""HTML Report Generator for contrast analysis results."""

from typing import Dict, Any


def generate_html_report(result: Dict[str, Any], output_path: str) -> None:
    """
    Generate HTML report with visual examples and WCAG status badges.

    Args:
        result: Analysis result dictionary from analyze_slide()
        output_path: Path to save HTML report
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contrast Analysis Report - Slide {result['slide_id']}</title>
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
    <h1>🎨 Contrast Analysis Report</h1>

    <div class="summary">
        <h2>Slide #{result['slide_id']}</h2>
        <p><strong>Background:</strong> {result['background']['source']}</p>
        <p><strong>Effective Background RGB:</strong>
            <span style="display: inline-block; width: 24px; height: 24px; background: rgb{result['background']['effective_rgb']}; border: 1px solid #ccc; vertical-align: middle; margin-right: 8px;"></span>
            rgb{result['background']['effective_rgb']}
        </p>
        <p><strong>ML Method:</strong> {result['ml_method']}</p>
        <p><strong>Total Entities:</strong> {result['summary']['total_entities']}</p>
        <p><strong>Passed AA Normal:</strong> <span class="status-pass">{result['summary']['passed_AA_normal']}</span></p>
        <p><strong>Failed AA Normal:</strong> <span class="status-fail">{result['summary']['failed_AA_normal']}</span></p>
    </div>
"""

    for ent in result['entities']:
        wcag = ent['contrast']['wcag']
        status = "✅ PASS" if wcag['AA_normal'] else "❌ FAIL"
        status_class = "status-pass" if wcag['AA_normal'] else "status-fail"

        html += f"""
    <div class="entity-card">
        <h3>{ent['id']} <span class="{status_class}">{status}</span></h3>

        <table>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Contrast Ratio (min)</td>
                <td><strong>{ent['contrast']['min_ratio']}:1</strong></td>
            </tr>
            <tr>
                <td>Contrast Ratio (max)</td>
                <td><strong>{ent['contrast']['max_ratio']}:1</strong></td>
            </tr>
            <tr>
                <td>Font Size</td>
                <td>{ent['font']['size_px']}px</td>
            </tr>
            <tr>
                <td>Font Weight</td>
                <td>{ent['font']['weight']}</td>
            </tr>
            <tr>
                <td>Is Large Text</td>
                <td>{'Yes' if ent['font']['is_large'] else 'No'}</td>
            </tr>
        </table>

        <div class="wcag-badges">
            <span class="badge badge-{'pass' if wcag['AA_normal'] else 'fail'}">
                AA Normal: {'✓' if wcag['AA_normal'] else '✗'}
            </span>
            <span class="badge badge-{'pass' if wcag['AA_large'] else 'fail'}">
                AA Large: {'✓' if wcag['AA_large'] else '✗'}
            </span>
            <span class="badge badge-{'pass' if wcag['AAA'] else 'fail'}">
                AAA: {'✓' if wcag['AAA'] else '✗'}
            </span>
        </div>

        <h4>Visual Previews:</h4>
        <div>
"""

        bg_rgb = result['background']['effective_rgb']
        for tc in ent['text_colors']:
            html += f"""
            <div class="preview-box" style="background: rgb{bg_rgb}; color: {tc['css']}; font-size: {ent['font']['size_px']}px; font-weight: {ent['font']['weight']};">
                Sample Text ({tc['css']})
            </div>
"""

        html += """
        </div>
"""

        # Add suggestions if failed
        if not wcag['AA_normal'] and ent.get('suggestions'):
            html += """
        <div class="suggestions">
            <h4>💡 Recommendations:</h4>
"""
            for sug in ent['suggestions']:
                expected_ratio_text = f"(Expected ratio: {sug['expected_ratio']}:1)" if sug.get('expected_ratio') else ""
                html += f"""
            <div class="suggestion-item">
                <strong>{sug['type']}:</strong> {sug['description']}<br>
                → <code>{sug['new_value']}</code> {expected_ratio_text}
            </div>
"""
            html += """
        </div>
"""

        html += """
    </div>
"""

    html += """
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
