"""A small in-memory task API used in the Copilot course."""

import re
from datetime import date, timedelta
from itertools import count
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    computed_field,
    field_validator,
)

app = FastAPI(title="Course Task API", version="0.1.0")


def _parse_iso_calendar_date(value: object, field_name: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if (
        not isinstance(value, str)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None
    ):
        raise ValueError(f"{field_name} must use YYYY-MM-DD format")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a valid calendar date") from error


def _parse_due_before(value: object) -> date | None:
    return _parse_iso_calendar_date(value, "due_before")


DueBeforeDate = Annotated[date | None, BeforeValidator(_parse_due_before)]


class TaskCreate(BaseModel):
    """Fields accepted when creating a task."""

    title: str = Field(min_length=1, max_length=120)
    completed: bool = False
    priority: Literal["low", "normal", "high"] = "normal"
    due_date: date | None = None
    labels: list[str] = Field(default_factory=list)
    dependency_ids: list[int] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def title_must_not_be_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must contain non-whitespace characters")
        return value

    @field_validator("labels", mode="before")
    @classmethod
    def normalize_labels(cls, value: object) -> list[str]:
        if not isinstance(value, list):
            raise ValueError("labels must be a list")
        if len(value) > 5:
            raise ValueError("labels must contain at most five items")

        normalized: list[str] = []
        seen: set[str] = set()
        for label in value:
            if not isinstance(label, str):
                raise ValueError("each label must be a string")
            label = label.strip()
            if not 1 <= len(label) <= 24:
                raise ValueError("each label must contain 1 to 24 characters")

            label = label.lower()
            if label not in seen:
                seen.add(label)
                normalized.append(label)
        return normalized

    @field_validator("due_date", mode="before")
    @classmethod
    def due_date_must_be_iso_calendar_date(cls, value: object) -> date | None:
        return _parse_iso_calendar_date(value, "due_date")

    @field_validator("dependency_ids")
    @classmethod
    def dependency_ids_must_be_unique(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("dependency_ids must not contain duplicates")
        return value


class Task(TaskCreate):
    """Task returned by the API."""

    id: int

    @computed_field
    @property
    def due_status(
        self,
    ) -> Literal["unscheduled", "completed", "overdue", "upcoming", "scheduled"]:
        if self.completed:
            return "completed"
        if self.due_date is None:
            return "unscheduled"

        today = date.today()
        if self.due_date < today:
            return "overdue"
        if self.due_date <= today + timedelta(days=7):
            return "upcoming"
        return "scheduled"


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
    label: str | None = None,
    due_status: Literal["upcoming", "overdue"] | None = None,
    due_before: DueBeforeDate = None,
) -> list[Task]:
    """Return tasks ordered high-first, optionally filtered by their fields."""

    normalized_label = label.strip().lower() if label is not None else None
    matches = [
        task
        for task in _tasks
        if (completed is None or task.completed == completed)
        and (priority is None or task.priority == priority)
        and (normalized_label is None or normalized_label in task.labels)
        and (due_status is None or task.due_status == due_status)
        and (
            due_before is None
            or (task.due_date is not None and task.due_date <= due_before)
        )
    ]
    # sorted() is stable, so equal-priority tasks keep their stored order.
    return sorted(matches, key=lambda task: _PRIORITY_RANK[task.priority])


@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(request: TaskCreate) -> Task:
    """Create a task and store it in memory."""

    existing_ids = {task.id for task in _tasks}
    unknown_ids = set(request.dependency_ids) - existing_ids
    if unknown_ids:
        raise HTTPException(
            status_code=422,
            detail=(
                "dependency_ids must reference existing tasks: "
                f"{sorted(unknown_ids)}"
            ),
        )

    task = Task(id=next(_task_ids), **request.model_dump())
    _tasks.append(task)
    return task
