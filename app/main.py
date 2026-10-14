from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import pymupdf
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.task_routes import router as task_router
from app.repositories.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor
from app.services.task_service import TaskService

app = FastAPI(
    title="Micro-API de resumo de PDF",
    description=(
        "Recebe PDFs digitais e gera resumos em DOCX do documento inteiro ou com base "
        "em uma senten\u00e7a orientadora, usando resumidor local e OpenAI opcional."
    ),
)
app.state.pdf_library = pymupdf
app.state.task_repository = TaskRepository()
app.state.priority_advisor = PriorityAdvisor()
app.state.task_service = TaskService(
    repository=app.state.task_repository,
    priority_advisor=app.state.priority_advisor,
)

app.include_router(task_router)


@app.get("/", include_in_schema=False)
async def frontend() -> FileResponse:
    """Serve the browser interface for PDF summary generation."""
    page = Path(__file__).parent / "static" / "index.html"
    return FileResponse(
        page,
        media_type="text/html; charset=utf-8",
        headers={"Cache-Control": "no-store, max-age=0"},
    )


class HealthResponse(BaseModel):
    status: Literal["ok"]
    timestamp: datetime


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return the API health status and current UTC timestamp."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
    )
