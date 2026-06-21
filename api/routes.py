from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from scraply.registry import ParserRegistry
from scraply.exporter import to_csv
import scraply.parsers  # noqa: F401 — triggers parser registration

router = APIRouter()


def _scrape(source: str, keyword: str, location: str, page: int) -> list:
    try:
        parser_cls = ParserRegistry.get(source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    parser = parser_cls()
    try:
        return parser.scrape(keyword, location, page)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/scrape")
def scrape_jobs(
    source: str = Query(..., description="Parser to use: jobstreet | indeed | kalibrr"),
    keyword: str = Query(..., description="Job title or keyword"),
    location: Optional[str] = Query("", description="City or region"),
    page: int = Query(1, ge=1, description="Result page number"),
    format: str = Query("json", description="Output format: json | csv"),
):
    jobs = _scrape(source, keyword, location, page)

    if format == "csv":
        content = to_csv(jobs)
        return StreamingResponse(
            io.StringIO(content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=jobs.csv"},
        )

    return {"source": source, "page": page, "count": len(jobs), "jobs": jobs}


@router.get("/sources")
def list_sources():
    return {"sources": ParserRegistry.available()}
