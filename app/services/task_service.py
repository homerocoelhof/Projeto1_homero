"""Regras de negócio para resumir PDFs e gerar documentos Word."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Protocol

import pymupdf
from docx import Document

from app.models.task import TaskCreate, TaskOut, TaskUpdate
from app.repositories.task_repository import TaskRepository


class PriorityAdvisor(Protocol):
    """Interface do componente que produz resumos orientados por sentença."""

    def summarize(self, source_text: str, sentence: str) -> str:
        """Gera um resumo usando o texto e a sentença como orientação."""
        ...


@dataclass(frozen=True)
class TaskResult:
    """Tarefa criada e conteúdo do documento Word gerado."""

    task: TaskOut
    document: bytes
    filename: str


class TaskProcessingError(Exception):
    """Erro controlado durante o processamento de uma tarefa."""


class TaskService:
    """Coordena extração do PDF, resumo e geração do documento."""

    def __init__(
        self,
        repository: TaskRepository,
        priority_advisor: PriorityAdvisor,
    ) -> None:
        self._repository = repository
        self._priority_advisor = priority_advisor

    def create_summary(self, pdf_path: str | Path, sentence: str) -> TaskResult:
        """Processa um PDF e retorna a tarefa e o resumo em formato DOCX."""
        path = Path(pdf_path).expanduser()
        normalized_sentence = sentence.strip()

        if not normalized_sentence:
            raise ValueError("A sentença orientadora não pode estar vazia.")
        if path.suffix.lower() != ".pdf":
            raise ValueError("O arquivo informado deve ter extensão .pdf.")
        if not path.is_file():
            raise ValueError("O arquivo PDF informado não existe ou não é um arquivo.")

        task = self._repository.create(
            TaskCreate(source_filename=path.name, sentence=normalized_sentence)
        )
        self._repository.update(task.id, TaskUpdate(status="processing"))

        try:
            source_text = self._extract_text(path)
            summary = self._priority_advisor.summarize(
                source_text=source_text,
                sentence=normalized_sentence,
            ).strip()
            if not summary:
                raise TaskProcessingError(
                    "O componente de resumo retornou conteúdo vazio."
                )

            document = self._create_docx(normalized_sentence, summary)
            completed = self._repository.update(
                task.id,
                TaskUpdate(status="completed", summary=summary),
            )
            if completed is None:
                raise TaskProcessingError(
                    "A tarefa deixou de existir durante o processamento."
                )

            return TaskResult(
                task=completed,
                document=document,
                filename=f"{path.stem}-resumo.docx",
            )
        except Exception as exc:
            self._repository.update(task.id, TaskUpdate(status="failed"))
            if isinstance(exc, TaskProcessingError):
                raise
            raise TaskProcessingError(
                "Não foi possível processar o arquivo PDF."
            ) from exc

    @staticmethod
    def _extract_text(pdf_path: Path) -> str:
        """Extrai texto de um PDF digital; não executa OCR."""
        try:
            with pymupdf.open(pdf_path) as pdf:
                text = "\n".join(page.get_text() for page in pdf).strip()
        except Exception as exc:
            raise TaskProcessingError(
                "O arquivo não é um PDF válido ou não pôde ser lido."
            ) from exc

        if not text:
            raise TaskProcessingError("O PDF não contém texto extraível.")
        return text

    @staticmethod
    def _create_docx(sentence: str, summary: str) -> bytes:
        """Cria em memória um DOCX com a sentença e o resumo."""
        document = Document()
        document.add_heading("Resumo do PDF", level=1)
        document.add_heading("Sentença orientadora", level=2)
        document.add_paragraph(sentence)
        document.add_heading("Resumo", level=2)
        document.add_paragraph(summary)

        output = BytesIO()
        document.save(output)
        return output.getvalue()
