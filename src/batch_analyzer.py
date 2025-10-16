"""Batch analyzer for processing multiple slides."""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional


def analyze_slide_batch(
    slides_dir: str = "examples/slides",
    output_dir: str = "output/batch",
    ml_method: str = "mediancut",
    verbose: bool = True
) -> List[Dict[str, Any]]:
    """
    Analyze all slide JSON files in a directory.

    Args:
        slides_dir: Directory containing slide JSON files
        output_dir: Directory to save analysis results
        ml_method: ML method to use (mediancut or kmeans)
        verbose: Print verbose output

    Returns:
        List of analysis results
    """
    slides_path = Path(slides_dir)
    if not slides_path.exists():
        raise FileNotFoundError(f"Slides directory not found: {slides_dir}")

    # Find all JSON files
    json_files = sorted(slides_path.glob("slide_*.json"))

    if not json_files:
        print(f"No slide JSON files found in {slides_dir}")
        return []

    print(f"Found {len(json_files)} slides to analyze")
    print(f"{'='*60}")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    for idx, json_file in enumerate(json_files, 1):
        print(f"\n[{idx}/{len(json_files)}] Analyzing {json_file.name}...")

        # Generate output filenames
        slide_name = json_file.stem  # e.g., "slide_001"
        result_json = output_path / f"{slide_name}_result.json"
        result_html = output_path / f"{slide_name}_report.html"

        # Build command
        cmd = [
            "python", "-m", "src.cli",
            "--slide-json", str(json_file),
            "--out-json", str(result_json),
            "--out-html", str(result_html),
            "--ml-method", ml_method
        ]

        if verbose:
            cmd.append("--verbose")

        # Run analysis
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # Load result
                with open(result_json, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)

                summary = analysis_data.get('summary', {})
                print(f"  [OK] Success!")
                print(f"    Total entities: {summary.get('total_entities', 0)}")
                print(f"    Passed AA: {summary.get('passed_AA_normal', 0)}")
                print(f"    Failed AA: {summary.get('failed_AA_normal', 0)}")

                results.append({
                    "slide_file": str(json_file),
                    "slide_id": analysis_data.get('slide_id'),
                    "summary": summary,
                    "result_json": str(result_json),
                    "result_html": str(result_html)
                })
            else:
                print(f"  [FAIL] Failed!")
                print(f"    Error: {result.stderr}")
                results.append({
                    "slide_file": str(json_file),
                    "error": result.stderr
                })

        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Timeout!")
            results.append({
                "slide_file": str(json_file),
                "error": "Analysis timed out"
            })
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            results.append({
                "slide_file": str(json_file),
                "error": str(e)
            })

    # Save batch summary
    summary_file = output_path / "batch_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"BATCH ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Total slides: {len(json_files)}")
    print(f"Successful: {sum(1 for r in results if 'error' not in r)}")
    print(f"Failed: {sum(1 for r in results if 'error' in r)}")
    print(f"\nResults saved to: {output_dir}/")
    print(f"Summary: {summary_file}")

    return results


def analyze_slide_batch_docker(
    slides_dir: str = "examples/slides",
    output_dir: str = "output/batch",
    ml_method: str = "mediancut",
    docker_image: str = "hse-contrast-checker"
) -> List[Dict[str, Any]]:
    """
    Analyze all slides using Docker container.

    Args:
        slides_dir: Directory containing slide JSON files
        output_dir: Directory to save analysis results
        ml_method: ML method to use
        docker_image: Docker image name

    Returns:
        List of analysis results
    """
    slides_path = Path(slides_dir)
    if not slides_path.exists():
        raise FileNotFoundError(f"Slides directory not found: {slides_dir}")

    json_files = sorted(slides_path.glob("slide_*.json"))

    if not json_files:
        print(f"No slide JSON files found in {slides_dir}")
        return []

    print(f"Found {len(json_files)} slides to analyze with Docker")
    print(f"{'='*60}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    # Get absolute paths
    slides_abs = slides_path.resolve()
    output_abs = output_path.resolve()

    for idx, json_file in enumerate(json_files, 1):
        print(f"\n[{idx}/{len(json_files)}] Analyzing {json_file.name}...")

        slide_name = json_file.stem
        result_json = f"/app/output/{slide_name}_result.json"
        result_html = f"/app/output/{slide_name}_report.html"

        # Build Docker command
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{slides_abs}:/app/slides",
            "-v", f"{output_abs}:/app/output",
            docker_image,
            "--slide-json", f"/app/slides/{json_file.name}",
            "--out-json", result_json,
            "--out-html", result_html,
            "--ml-method", ml_method,
            "--verbose"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                # Load result
                local_result = output_path / f"{slide_name}_result.json"
                with open(local_result, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)

                summary = analysis_data.get('summary', {})
                print(f"  [OK] Success!")
                print(f"    Total entities: {summary.get('total_entities', 0)}")
                print(f"    Passed AA: {summary.get('passed_AA_normal', 0)}")
                print(f"    Failed AA: {summary.get('failed_AA_normal', 0)}")

                results.append({
                    "slide_file": str(json_file),
                    "slide_id": analysis_data.get('slide_id'),
                    "summary": summary,
                    "result_json": str(local_result),
                    "result_html": str(output_path / f"{slide_name}_report.html")
                })
            else:
                print(f"  [FAIL] Failed!")
                print(f"    Error: {result.stderr}")
                results.append({
                    "slide_file": str(json_file),
                    "error": result.stderr
                })

        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Timeout!")
            results.append({
                "slide_file": str(json_file),
                "error": "Analysis timed out"
            })
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            results.append({
                "slide_file": str(json_file),
                "error": str(e)
            })

    # Save batch summary
    summary_file = output_path / "batch_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"DOCKER BATCH ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Total slides: {len(json_files)}")
    print(f"Successful: {sum(1 for r in results if 'error' not in r)}")
    print(f"Failed: {sum(1 for r in results if 'error' in r)}")
    print(f"\nResults saved to: {output_dir}/")
    print(f"Summary: {summary_file}")

    return results


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Batch analyze multiple slides")
    parser.add_argument("slides_dir", help="Directory containing slide JSON files")
    parser.add_argument("--output-dir", default="output/batch", help="Output directory")
    parser.add_argument("--ml-method", default="mediancut", choices=["mediancut", "kmeans"], help="ML method")
    parser.add_argument("--docker", action="store_true", help="Use Docker for analysis")
    parser.add_argument("--docker-image", default="hse-contrast-checker", help="Docker image name")

    args = parser.parse_args()

    try:
        if args.docker:
            results = analyze_slide_batch_docker(
                args.slides_dir,
                args.output_dir,
                args.ml_method,
                args.docker_image
            )
        else:
            results = analyze_slide_batch(
                args.slides_dir,
                args.output_dir,
                args.ml_method
            )

        # Print final summary
        if results:
            total_entities = sum(r.get('summary', {}).get('total_entities', 0) for r in results if 'error' not in r)
            passed_aa = sum(r.get('summary', {}).get('passed_AA_normal', 0) for r in results if 'error' not in r)
            failed_aa = sum(r.get('summary', {}).get('failed_AA_normal', 0) for r in results if 'error' not in r)

            print(f"\nACROSS ALL SLIDES:")
            print(f"  Total text entities: {total_entities}")
            print(f"  Passed AA Normal: {passed_aa}")
            print(f"  Failed AA Normal: {failed_aa}")

            if total_entities > 0:
                pass_rate = (passed_aa / total_entities) * 100
                print(f"  Pass rate: {pass_rate:.1f}%")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
