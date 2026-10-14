"""Business rules for summarizing PDFs and generating Word documents."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import Protocol

import pymupdf
from docx import Document

from app.models.task import TaskCreate, TaskOut, TaskUpdate
from app.repositories.task_repository import TaskRepository


class PriorityAdvisor(Protocol):
    def summarize(self, source_text: str, sentence: str | None) -> str: ...


@dataclass(frozen=True)
class TaskResult:
    task: TaskOut
    document: bytes
    filename: str


class TaskProcessingError(Exception):
    """Controlled error during task processing."""


class TaskService:
    """Coordinates PDF extraction, summary generation, and DOCX creation."""

    def __init__(self, repository: TaskRepository, priority_advisor: PriorityAdvisor) -> None:
        self._repository = repository
        self._priority_advisor = priority_advisor
        self._filename_lock = Lock()
        self._filename_counters: dict[str, int] = {}

    def create_summary(
        self,
        pdf_path: str | Path,
        sentence: str | None = None,
        *,
        summary_mode: str = "guided",
    ) -> TaskResult:
        """Create a sentence-guided or full-document summary as a DOCX."""
        path = Path(pdf_path).expanduser()
        normalized_sentence = sentence.strip() if sentence else None
        if summary_mode not in {"guided", "whole"}:
            raise ValueError("Modo de resumo inválido.")
        if summary_mode == "guided" and not normalized_sentence:
            raise ValueError("A sentença orientadora não pode estar vazia.")
        if path.suffix.lower() != ".pdf":
            raise ValueError("O arquivo informado deve ter extensão .pdf.")
        if not path.is_file():
            raise ValueError("O arquivo PDF informado não existe ou não é um arquivo.")

        task = self._repository.create(
            TaskCreate(
                source_filename=path.name,
                summary_mode=summary_mode,
                sentence=normalized_sentence if summary_mode == "guided" else None,
            )
        )
        self._repository.update(task.id, TaskUpdate(status="processing"))

        try:
            source_text = self._extract_text(path)
            if summary_mode == "guided":
                normalized_source = self._normalize_for_search(source_text)
                normalized_query = self._normalize_for_search(normalized_sentence or "")
                if normalized_query not in normalized_source:
                    raise TaskProcessingError(
                        f"A sentença não foi encontrada no arquivo '{path.name}'."
                    )

            summary = self._priority_advisor.summarize(
                source_text=source_text,
                sentence=normalized_sentence if summary_mode == "guided" else None,
            ).strip()
            if not summary:
                raise TaskProcessingError("O componente de resumo retornou conteúdo vazio.")

            document = self._create_docx(
                normalized_sentence or "Documento inteiro",
                summary,
                heading="Sentença orientadora" if summary_mode == "guided" else "Escopo do resumo",
            )
            completed = self._repository.update(
                task.id,
                TaskUpdate(status="completed", summary=summary),
            )
            if completed is None:
                raise TaskProcessingError("A tarefa deixou de existir durante o processamento.")

            return TaskResult(
                task=completed,
                document=document,
                filename=self._next_output_filename(path.stem),
            )
        except Exception as exc:
            self._repository.update(task.id, TaskUpdate(status="failed"))
            if isinstance(exc, TaskProcessingError):
                raise
            raise TaskProcessingError("Não foi possível processar o arquivo PDF.") from exc

    @staticmethod
    def _normalize_for_search(text: str) -> str:
        return " ".join(text.casefold().split())

    def _next_output_filename(self, source_stem: str) -> str:
        key = source_stem.casefold()
        with self._filename_lock:
            next_number = self._filename_counters.get(key, 0) + 1
            self._filename_counters[key] = next_number
        return f"{source_stem}_{next_number}.docx"

    @staticmethod
    def _extract_text(pdf_path: Path) -> str:
        try:
            with pymupdf.open(pdf_path) as pdf:
                text = "\n".join(page.get_text() for page in pdf).strip()
        except Exception as exc:
            raise TaskProcessingError("O arquivo não é um PDF válido ou não pôde ser lido.") from exc
        if not text:
            raise TaskProcessingError("O PDF não contém texto extraível.")
        return text

    @staticmethod
    def _create_docx(scope: str, summary: str, *, heading: str) -> bytes:
        document = Document()
        document.add_heading("Resumo do PDF", level=1)
        document.add_heading(heading, level=2)
        document.add_paragraph(scope)
        document.add_heading("Resumo", level=2)
        document.add_paragraph(summary)
        output = BytesIO()
        document.save(output)
        return output.getvalue()
