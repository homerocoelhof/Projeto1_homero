from pathlib import Path
from types import SimpleNamespace

import pytest

from app.repositories.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor
from app.services.task_service import TaskService


class FailingResponses:
    def create(self, **kwargs: object) -> object:
        raise RuntimeError("Falha simulada no provedor externo")


@pytest.fixture
def failing_client() -> SimpleNamespace:
    return SimpleNamespace(responses=FailingResponses())


def test_summarize_uses_local_heuristic_when_sentence_has_no_matching_terms() -> None:
    source_text = (
        "Primeira sentença sobre astronomia. "
        "Segunda sentença sobre biologia. "
        "Terceira sentença sobre geografia."
    )

    summary = PriorityAdvisor().summarize(
        source_text=source_text,
        sentence="Explique o tópico de culinária.",
    )

    # Sem termos em comum, a heurística local seleciona as primeiras sentenças.
    assert summary == source_text


def test_summarize_uses_local_fallback_when_external_call_fails(
    failing_client: SimpleNamespace,
) -> None:
    advisor = PriorityAdvisor(
        api_key="chave-de-teste",
        model="modelo-de-teste",
        client=failing_client,
    )
    source_text = (
        "A fotossíntese ocorre nas plantas. "
        "A respiração celular libera energia."
    )

    summary = advisor.summarize(
        source_text=source_text,
        sentence="Como ocorre a fotossíntese?",
    )

    assert summary == "A fotossíntese ocorre nas plantas."


def test_summarize_rejects_empty_source_text() -> None:
    with pytest.raises(ValueError, match="texto de origem não pode estar vazio"):
        PriorityAdvisor().summarize(
            source_text="   ",
            sentence="Qual é o assunto?",
        )


def test_task_service_rejects_nonexistent_pdf(tmp_path: Path) -> None:
    service = TaskService(
        repository=TaskRepository(),
        priority_advisor=PriorityAdvisor(),
    )
    missing_pdf = tmp_path / "nao-existe.pdf"

    with pytest.raises(ValueError, match="não existe ou não é um arquivo"):
        service.create_summary(missing_pdf, "Qual é o assunto?")
