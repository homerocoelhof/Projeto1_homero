import pymupdf
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.task_routes import router
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService


class FakePriorityAdvisor:
    def summarize(self, source_text: str, sentence: str) -> str:
        return "Resumo de teste."


@pytest.fixture
def pdf_bytes() -> bytes:
    """Gera um PDF digital pequeno para testar o endpoint de criação."""
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((72, 72), "Conteúdo de teste. Qual é o assunto?")
        return pdf.tobytes()


@pytest.fixture
def client() -> TestClient:
    """Cria uma aplicação e dependências isoladas para cada teste."""
    app = FastAPI()
    app.include_router(router)

    repository = TaskRepository()
    app.state.task_repository = repository
    app.state.task_service = TaskService(
        repository=repository,
        priority_advisor=FakePriorityAdvisor(),
    )

    with TestClient(app) as test_client:
        yield test_client


def test_task_crud_returns_expected_status_codes(
    client: TestClient,
    pdf_bytes: bytes,
) -> None:
    create_response = client.post(
        "/tasks",
        files={"file": ("documento.pdf", pdf_bytes, "application/pdf")},
        data={"sentence": "Qual é o assunto?"},
    )

    assert create_response.status_code == 201
    assert create_response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    task_id = create_response.headers["x-task-id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == task_id
    assert get_response.json()["status"] == "completed"

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert any(task["id"] == task_id for task in list_response.json())

    update_response = client.put(
        f"/tasks/{task_id}",
        json={"summary": "Resumo atualizado."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["summary"] == "Resumo atualizado."

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""


def test_get_task_returns_404_for_nonexistent_id(client: TestClient) -> None:
    response = client.get("/tasks/id-inexistente")

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarefa não encontrada."}
