"""Command Line Interface for HSE ML Contrast Checker."""

import click
import json
from pathlib import Path
import sys

from src.contrast_checker import analyze_slide
from src.report_generator import generate_html_report


@click.command()
@click.option("--slide-json", required=True, type=click.Path(exists=True), help="Path to slide JSON file")
@click.option("--slide-index", type=int, default=None, help="If JSON is array, index of slide to analyze (default: 0)")
@click.option("--bg-image", type=click.Path(exists=True), default=None, help="Optional background image file")
@click.option(
    "--ml-method",
    type=click.Choice(["mediancut", "kmeans"], case_sensitive=False),
    default="mediancut",
    help="ML method for dominant colors extraction (default: mediancut)",
)
@click.option("--k-colors", type=int, default=5, help="Number of dominant colors to extract (default: 5)")
@click.option(
    "--out-json",
    type=click.Path(),
    default="output/result.json",
    help="Output JSON file path (default: output/result.json)",
)
@click.option(
    "--out-html",
    type=click.Path(),
    default="output/report.html",
    help="Output HTML report path (default: output/report.html)",
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(slide_json, slide_index, bg_image, ml_method, k_colors, out_json, out_html, verbose):
    """
    HSE ML Contrast Checker - Analyze text/background contrast using ML.

    This tool analyzes contrast between text and background colors according
    to WCAG 2.2 accessibility standards. It uses machine learning algorithms
    (median-cut or K-means) to extract dominant colors from background images.

    Examples:

    \b
        # Analyze slide with color background
        python -m src.cli --slide-json examples/slide_color_bg.json

    \b
        # Analyze slide with image background using K-means
        python -m src.cli --slide-json examples/slide_with_image.json \\
            --bg-image examples/background.png --ml-method kmeans

    \b
        # Custom output paths
        python -m src.cli --slide-json examples/slide_complex.json \\
            --out-json results/my_result.json --out-html results/my_report.html
    """
    try:
        if verbose:
            click.echo(f"Loading slide from: {slide_json}")
            click.echo(f"ML method: {ml_method}")
            if bg_image:
                click.echo(f"Background image: {bg_image}")

        # Analyze slide
        if verbose:
            click.echo("Analyzing contrast...")

        result = analyze_slide(
            slide_json_path=slide_json,
            slide_index=slide_index,
            bg_image_path=bg_image,
            ml_method=ml_method,
            k_colors=k_colors,
        )

        # Save JSON result
        out_json_path = Path(out_json)
        out_json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if verbose:
            click.echo(f"JSON saved to: {out_json_path}")

        # Generate HTML report
        out_html_path = Path(out_html)
        out_html_path.parent.mkdir(parents=True, exist_ok=True)

        generate_html_report(result, str(out_html_path))

        if verbose:
            click.echo(f"HTML report saved to: {out_html_path}")

        # Print summary
        click.echo()
        click.secho("Analysis complete!", fg="green", bold=True)
        click.echo(f"  Slide ID: {result['slide_id']}")
        click.echo(f"  Total entities: {result['summary']['total_entities']}")
        click.echo(f"  Passed AA Normal: {result['summary']['passed_AA_normal']}")
        click.echo(f"  Failed AA Normal: {result['summary']['failed_AA_normal']}")
        click.echo()
        click.echo(f"  JSON: {out_json_path}")
        click.echo(f"  HTML: {out_html_path}")

        # Exit code based on WCAG compliance
        if result["summary"]["failed_AA_normal"] > 0:
            click.echo()
            click.secho(
                f"Warning: {result['summary']['failed_AA_normal']} entity(ies) failed WCAG AA Normal standard",
                fg="yellow",
            )
            sys.exit(1)

    except FileNotFoundError as e:
        click.secho(f"Error: File not found - {e}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(2)

    except ValueError as e:
        click.secho(f"Error: Invalid data - {e}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(2)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
