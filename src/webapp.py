"""FastAPI Web Application for HSE ML Contrast Checker."""

import os
import json
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from src.slide_scraper_advanced import scrape_all_slides_from_url, scrape_all_slides_from_file
from src.contrast_checker import analyze_slide
from src.report_generator import generate_html_report


app = FastAPI(
    title="HSE ML Contrast Checker",
    description="Анализ контрастности слайдов с использованием ML",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
STATIC_DIR = Path(__file__).parent.parent / "static"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "web_output"

STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/results", StaticFiles(directory=str(OUTPUT_DIR)), name="results")


class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint."""
    url: Optional[HttpUrl] = None
    ml_method: Literal["kmeans", "mediancut"] = "mediancut"
    slide_mode: Literal["single", "all"] = "single"
    slide_index: Optional[int] = 1


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the landing page."""
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse(content="<h1>Landing page not found</h1>", status_code=404)

    return FileResponse(index_file)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "HSE ML Contrast Checker"}


@app.post("/api/analyze-url")
async def analyze_url(
    url: str = Form(...),
    ml_method: str = Form("mediancut"),
    slide_mode: str = Form("single"),
    slide_index: int = Form(1)
):
    """
    Analyze slides from URL using Selenium.

    Args:
        url: URL to Diaclass presentation
        ml_method: ML method (kmeans or mediancut)
        slide_mode: 'single' for one slide, 'all' for entire presentation
        slide_index: Index of slide to analyze (1-based) if slide_mode is 'single'
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(exist_ok=True)

        # Scrape slides
        if slide_mode == "single":
            slides = scrape_all_slides_from_url(
                url=url,
                output_dir=str(session_dir / "slides"),
                use_selenium=True,
                wait_time=5,
                slide_index=slide_index
            )
        else:
            slides = scrape_all_slides_from_url(
                url=url,
                output_dir=str(session_dir / "slides"),
                use_selenium=True,
                wait_time=5
            )

        if not slides:
            raise HTTPException(status_code=400, detail="Не удалось извлечь слайды")

        # Find all slide JSON files in the directory
        slides_dir = session_dir / "slides"
        slide_json_files = sorted(slides_dir.glob("slide_*.json"))

        if not slide_json_files:
            raise HTTPException(status_code=400, detail="Не удалось найти извлечённые слайды")

        # Analyze each slide
        results = []
        for display_idx, slide_json_path in enumerate(slide_json_files, 1):
            # Analyze
            result = analyze_slide(
                slide_json_path=str(slide_json_path),
                ml_method=ml_method,
                k_colors=5
            )

            # Generate HTML report
            report_path = session_dir / f"report_{display_idx:03d}.html"
            generate_html_report(result, str(report_path))

            # Save JSON result
            json_path = session_dir / f"result_{display_idx:03d}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            results.append({
                "slide_id": result["slide_id"],
                "slide_number": display_idx,
                "summary": result["summary"],
                "report_url": f"/results/{session_id}/report_{display_idx:03d}.html",
                "json_url": f"/results/{session_id}/result_{display_idx:03d}.json"
            })

        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "total_slides": len(results),
            "results": results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")


@app.post("/api/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    ml_method: str = Form("mediancut"),
    slide_mode: str = Form("single"),
    slide_index: int = Form(1)
):
    """
    Analyze slides from uploaded HTML file.

    Args:
        file: HTML file with slides
        ml_method: ML method (kmeans or mediancut)
        slide_mode: 'single' for one slide, 'all' for entire presentation
        slide_index: Index of slide to analyze (1-based) if slide_mode is 'single'
    """
    try:
        # Validate file type
        if not file.filename.endswith('.html'):
            raise HTTPException(status_code=400, detail="Только HTML файлы разрешены")

        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(exist_ok=True)

        # Save uploaded file
        temp_html = session_dir / "uploaded.html"
        content = await file.read()
        temp_html.write_bytes(content)

        # Scrape slides
        if slide_mode == "single":
            slides = scrape_all_slides_from_file(
                file_path=str(temp_html),
                output_dir=str(session_dir / "slides"),
                slide_index=slide_index
            )
        else:
            slides = scrape_all_slides_from_file(
                file_path=str(temp_html),
                output_dir=str(session_dir / "slides")
            )

        if not slides:
            raise HTTPException(status_code=400, detail="Не удалось извлечь слайды")

        # Find all slide JSON files in the directory
        slides_dir = session_dir / "slides"
        slide_json_files = sorted(slides_dir.glob("slide_*.json"))

        if not slide_json_files:
            raise HTTPException(status_code=400, detail="Не удалось найти извлечённые слайды")

        # Analyze each slide
        results = []
        for display_idx, slide_json_path in enumerate(slide_json_files, 1):
            # Analyze
            result = analyze_slide(
                slide_json_path=str(slide_json_path),
                ml_method=ml_method,
                k_colors=5
            )

            # Generate HTML report
            report_path = session_dir / f"report_{display_idx:03d}.html"
            generate_html_report(result, str(report_path))

            # Save JSON result
            json_path = session_dir / f"result_{display_idx:03d}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            results.append({
                "slide_id": result["slide_id"],
                "slide_number": display_idx,
                "summary": result["summary"],
                "report_url": f"/results/{session_id}/report_{display_idx:03d}.html",
                "json_url": f"/results/{session_id}/result_{display_idx:03d}.json"
            })

        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "total_slides": len(results),
            "results": results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")


@app.get("/api/result/{session_id}/{filename}")
async def get_result(session_id: str, filename: str):
    """Get analysis result file."""
    file_path = OUTPUT_DIR / session_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")

    if filename.endswith('.json'):
        return FileResponse(file_path, media_type="application/json")
    elif filename.endswith('.html'):
        return FileResponse(file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип файла")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
