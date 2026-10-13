"""Rotas HTTP para criação e manutenção de tarefas de resumo."""

from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from starlette.concurrency import run_in_threadpool

from app.models.task import TaskOut, TaskUpdate
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskProcessingError, TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_repository(request: Request) -> TaskRepository:
    """Obtém o repositório configurado na aplicação."""
    return request.app.state.task_repository


def _get_service(request: Request) -> TaskService:
    """Obtém o serviço configurado na aplicação."""
    return request.app.state.task_service


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    file: UploadFile = File(..., description="Arquivo PDF digital."),
    sentence: str = Form(..., min_length=1, description="Sentença orientadora."),
) -> StreamingResponse:
    """Gera resumo e retorna o DOCX; o ID da tarefa vem no cabeçalho."""
    original_name = (file.filename or "").replace("\\", "/")
    safe_name = Path(original_name).name
    if not safe_name or Path(safe_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo com extensão .pdf.",
        )

    try:
        with TemporaryDirectory(prefix="pdf-summary-") as temp_dir:
            temp_path = Path(temp_dir) / safe_name
            with temp_path.open("wb") as destination:
                while chunk := await file.read(1024 * 1024):
                    destination.write(chunk)

            result = await run_in_threadpool(
                _get_service(request).create_summary,
                temp_path,
                sentence,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except TaskProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()

    encoded_filename = quote(result.filename)
    return StreamingResponse(
        iter([result.document]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        status_code=status.HTTP_201_CREATED,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "X-Task-ID": result.task.id,
        },
    )


@router.get("", response_model=list[TaskOut])
def list_tasks(request: Request) -> list[TaskOut]:
    """Lista tarefas armazenadas em memória."""
    return _get_repository(request).list()


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str, request: Request) -> TaskOut:
    """Retorna uma tarefa ou responde 404 se ela não existir."""
    task = _get_repository(request).get_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada.",
        )
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: str,
    changes: TaskUpdate,
    request: Request,
) -> TaskOut:
    """Atualiza uma tarefa existente ou responde 404."""
    task = _get_repository(request).update(task_id, changes)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada.",
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, request: Request) -> Response:
    """Remove uma tarefa ou responde 404 se ela não existir."""
    deleted = _get_repository(request).delete(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
