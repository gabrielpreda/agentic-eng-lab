"""A small in-memory task API used in the Copilot course."""

from itertools import count
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Course Task API", version="0.1.0")


class TaskCreate(BaseModel):
    """Fields accepted when creating a task."""

    title: str = Field(min_length=1, max_length=120)
    completed: bool = False
    priority: Literal["low", "normal", "high"] = "normal"

    @field_validator("title")
    @classmethod
    def title_must_not_be_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must contain non-whitespace characters")
        return value


class Task(TaskCreate):
    """Task returned by the API."""

    id: int


_PRIORITY_RANK = {"high": 0, "normal": 1, "low": 2}

_tasks: list[Task] = []
_task_ids = count(1)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Report that the service is running."""

    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
async def list_tasks(
    completed: bool | None = None,
    priority: Literal["low", "normal", "high"] | None = None,
) -> list[Task]:
    """Return tasks ordered high-first, optionally filtered by completion and priority."""

    matches = [
        task
        for task in _tasks
        if (completed is None or task.completed == completed)
        and (priority is None or task.priority == priority)
    ]
    # sorted() is stable, so equal-priority tasks keep their stored order.
    return sorted(matches, key=lambda task: _PRIORITY_RANK[task.priority])


@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(request: TaskCreate) -> Task:
    """Create a task and store it in memory."""

    task = Task(id=next(_task_ids), **request.model_dump())
    _tasks.append(task)
    return task
