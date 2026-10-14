"""Modelos de dados para solicitações de resumo de PDF."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class TaskCreate(BaseModel):
    """Dados necessários para criar uma tarefa de resumo."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    source_filename: str = Field(
        min_length=1,
        max_length=255,
        description="Nome do arquivo PDF enviado.",
    )
    summary_mode: Literal["guided", "whole"] = "guided"
    sentence: str | None = Field(
        default=None,
        max_length=2_000,
        description="Sentença que orienta o foco do resumo, quando aplicável.",
    )


class TaskUpdate(BaseModel):
    """Campos alteráveis de uma tarefa de resumo."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=32,
        description="Estado atual da tarefa.",
    )
    summary: str | None = Field(
        default=None,
        min_length=1,
        description="Resumo gerado a partir do PDF.",
    )
    document_url: HttpUrl | None = Field(
        default=None,
        description="URL do documento Word gerado.",
    )


class TaskOut(BaseModel):
    """Representação pública de uma tarefa de resumo."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(min_length=1, description="Identificador da tarefa.")
    source_filename: str = Field(min_length=1, max_length=255)
    summary_mode: Literal["guided", "whole"] = "guided"
    sentence: str | None = Field(default=None, max_length=2_000)
    status: str = Field(min_length=1, max_length=32)
    summary: str | None = None
    document_url: HttpUrl | None = None
