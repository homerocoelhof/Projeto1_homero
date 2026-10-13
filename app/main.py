from datetime import datetime, timezone
from typing import Literal

import pymupdf
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="PDF Summary API")
app.state.pdf_library = pymupdf


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

