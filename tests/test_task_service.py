from io import BytesIO
from pathlib import Path

import pymupdf
import pytest
from docx import Document
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.task_routes import router
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskProcessingError, TaskService


class FakePriorityAdvisor:
    """Substitui o resumidor externo por uma resposta previsível."""

    def summarize(self, source_text: str, sentence: str) -> str:
        assert "Texto de exemplo extraído do PDF." in source_text
        assert sentence == "Qual é o assunto principal?"
        return "Este é um resumo de exemplo."


@pytest.fixture
def pdf_path(tmp_path: Path) -> Path:
    """Cria um PDF digital pequeno para os testes."""
    path = tmp_path / "documento.pdf"
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text(
            (72, 72),
            "Texto de exemplo extraído do PDF. Qual é o assunto principal?",
        )
        pdf.save(path)
    return path


@pytest.fixture
def repository() -> TaskRepository:
    return TaskRepository()


@pytest.fixture
def service(repository: TaskRepository) -> TaskService:
    return TaskService(
        repository=repository,
        priority_advisor=FakePriorityAdvisor(),
    )


def test_create_summary_extracts_pdf_and_generates_word_document(
    service: TaskService,
    repository: TaskRepository,
    pdf_path: Path,
) -> None:
    result = service.create_summary(pdf_path, "Qual é o assunto principal?")

    assert result.task.status == "completed"
    assert result.task.source_filename == "documento.pdf"
    assert result.task.summary == "Este é um resumo de exemplo."
    assert result.filename == "documento_1.docx"
    assert repository.get_by_id(result.task.id) == result.task

    document = Document(BytesIO(result.document))
    document_text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert "Qual é o assunto principal?" in document_text
    assert "Este é um resumo de exemplo." in document_text


def test_output_filename_number_increments_for_same_pdf(
    service: TaskService,
    pdf_path: Path,
) -> None:
    first_result = service.create_summary(pdf_path, "Qual é o assunto principal?")
    second_result = service.create_summary(pdf_path, "Qual é o assunto principal?")

    assert first_result.filename == "documento_1.docx"
    assert second_result.filename == "documento_2.docx"


def test_create_summary_fails_when_sentence_is_not_in_pdf(
    service: TaskService,
    repository: TaskRepository,
    pdf_path: Path,
) -> None:
    with pytest.raises(TaskProcessingError, match="A sentença não foi encontrada"):
        service.create_summary(pdf_path, "Uma sentença que não existe no PDF")

    tasks = repository.list()
    assert len(tasks) == 1
    assert tasks[0].status == "failed"


def test_get_task_returns_404_for_nonexistent_id(repository: TaskRepository) -> None:
    app = FastAPI()
    app.include_router(router)
    app.state.task_repository = repository

    with TestClient(app) as client:
        response = client.get("/tasks/id-inexistente")

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarefa não encontrada."}
