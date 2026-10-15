from pathlib import Path
from types import SimpleNamespace

import pytest

from app.repositories.task_repository import TaskRepository
from app.services.priority_advisor import PriorityAdvisor
from app.services.task_service import TaskService


class FailingResponses:
    def create(self, **kwargs: object) -> object:
        raise RuntimeError("Falha simulada no provedor externo")


class RecordingResponses:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


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


def test_summarize_whole_document_selects_sentences_across_the_source() -> None:
    source_text = " ".join(
        f"Sentença {index} descreve o tópico número {index}."
        for index in range(1, 14)
    )

    summary = PriorityAdvisor().summarize(source_text=source_text, sentence=None)

    assert "Sentença 1" in summary
    assert "Sentença 7" in summary
    assert "Sentença 13" in summary
    assert len(summary) < len(source_text)


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


@pytest.mark.parametrize(
    ("sentence", "expected_heading", "expected_word_limit", "expected_tokens"),
    [
        ("Qual o efeito da medida?", "Resposta à sentença", 350, 1_050),
        (None, "Assunto principal do PDF", 350, 1_050),
    ],
)
def test_openai_summary_requests_concise_representative_answer(
    sentence: str | None,
    expected_heading: str,
    expected_word_limit: int,
    expected_tokens: int,
) -> None:
    source_text = (
        "A medida reduziu o consumo de energia nas escolas. "
        "O relatório compara os resultados de três regiões e recomenda ampliar "
        "a iniciativa onde houve maior economia."
    )
    expected_summary = (
        f"## {expected_heading}\nA medida reduziu o consumo de energia; "
        "o relatório recomenda ampliá-la nas regiões com maior economia."
    )
    responses = RecordingResponses(expected_summary)
    advisor = PriorityAdvisor(
        api_key="chave-de-teste",
        client=SimpleNamespace(responses=responses),
    )

    summary = advisor.summarize(source_text, sentence)

    assert summary == expected_summary
    assert len(responses.calls) == 2
    call = responses.calls[0]
    review_call = responses.calls[1]
    assert call["max_output_tokens"] == expected_tokens
    assert f"{expected_word_limit} palavras" in call["instructions"]
    assert "semânt" in call["instructions"]
    assert "metodologia" in call["instructions"]
    assert "termos-chave" in call["instructions"]
    assert "perguntas de prova" in call["instructions"]
    assert source_text in call["input"]
    assert "verificação semântica" in review_call["instructions"]
    assert source_text in review_call["input"]
    assert expected_summary in review_call["input"]
    if sentence:
        assert sentence in call["input"]
        assert "sentença orientadora" in call["instructions"]
    else:
        assert "documento completo" in call["instructions"]


def test_task_service_rejects_nonexistent_pdf(tmp_path: Path) -> None:
    service = TaskService(
        repository=TaskRepository(),
        priority_advisor=PriorityAdvisor(),
    )
    missing_pdf = tmp_path / "nao-existe.pdf"

    with pytest.raises(ValueError, match="não existe ou não é um arquivo"):
        service.create_summary(missing_pdf, "Qual é o assunto?")
