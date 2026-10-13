"""Repositório em memória para tarefas de resumo de PDF."""

from threading import RLock
from uuid import uuid4

from app.models.task import TaskCreate, TaskOut, TaskUpdate


class TaskRepository:
    """Armazena tarefas em memória durante a execução do processo."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskOut] = {}
        self._lock = RLock()

    def create(self, task: TaskCreate) -> TaskOut:
        """Cria uma tarefa e retorna sua representação pública."""
        task_id = str(uuid4())
        created = TaskOut(
            id=task_id,
            source_filename=task.source_filename,
            sentence=task.sentence,
            status="pending",
        )

        with self._lock:
            self._tasks[task_id] = created
            return created.model_copy(deep=True)

    def list(self) -> list[TaskOut]:
        """Retorna uma cópia de todas as tarefas."""
        with self._lock:
            return [task.model_copy(deep=True) for task in self._tasks.values()]

    def get_by_id(self, task_id: str) -> TaskOut | None:
        """Retorna uma tarefa pelo ID, ou None se não existir."""
        with self._lock:
            task = self._tasks.get(task_id)
            return task.model_copy(deep=True) if task is not None else None

    def update(self, task_id: str, changes: TaskUpdate) -> TaskOut | None:
        """Atualiza os campos enviados e retorna a tarefa, se existir."""
        with self._lock:
            current = self._tasks.get(task_id)
            if current is None:
                return None

            updated = current.model_copy(
                update=changes.model_dump(exclude_unset=True),
                deep=True,
            )
            self._tasks[task_id] = updated
            return updated.model_copy(deep=True)

    def delete(self, task_id: str) -> bool:
        """Remove a tarefa e indica se ela existia."""
        with self._lock:
            return self._tasks.pop(task_id, None) is not None
