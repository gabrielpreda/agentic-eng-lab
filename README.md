# Task API — Module 1 starter

A deliberately small in-memory FastAPI application for the Agentic Engineering with GitHub Copilot course. This is a learning target, not a production service.

## Requirements

- Python 3.10 or later

## Install and run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> to try the API.

## API contract

### `GET /healthz`

Returns `200 OK` when the service is running:

```json
{"status": "ok"}
```

### `GET /tasks`

Returns `200 OK` with a JSON array of tasks. Each task has this shape:

```json
{
  "id": 1,
  "title": "Write documentation",
  "completed": false,
  "priority": "normal",
  "due_date": "2026-12-01",
  "due_status": "upcoming",
  "labels": ["project"],
  "dependency_ids": []
}
```

The array is empty when there are no tasks. To filter tasks by completion status, use `?completed=true` or `?completed=false`. To filter by priority, use `?priority=low`, `?priority=normal`, or `?priority=high`; other priority values are rejected with `422`. To see tasks due soon or already late, use `?due_status=upcoming` or `?due_status=overdue`; other values are rejected with `422`. Upcoming includes incomplete tasks due today through the next seven calendar days, inclusive. Overdue includes incomplete tasks due before today. The `completed`, `priority`, and `due_status` filters can be combined, and only tasks matching every supplied filter are returned. Without these query parameters, all tasks are returned. Tasks are always ordered by priority: `high`, then `normal`, then `low`.

To filter by a label, use `?label=project`. The query is trimmed and lowercased before matching; labels match exactly. A task is returned once if its normalized labels include the chosen label. If no tasks match, the response is `200 OK` with an empty array. The label filter can be combined with the other task filters.

To select tasks due on or before a specific date, use `?due_before=YYYY-MM-DD`. The date is inclusive; tasks without a due date are excluded, while completed tasks are included unless narrowed by `completed`. This filter can be combined with `completed`, `priority`, `due_status`, and `label`. The selected date must be a valid ISO calendar date; invalid values are rejected with `422`.

Each task includes `due_date`, `due_status`, `labels`, and `dependency_ids`. A missing due date is returned as `null` and has status `unscheduled`. Completed tasks have status `completed`; incomplete tasks are `overdue` when their date has passed, `upcoming` when due within seven days (including today), or `scheduled` when due later. Status is computed using the server's current calendar date. Tasks created without labels or dependencies have empty `labels` and `dependency_ids` arrays.

### `POST /tasks`

Create a task by sending a JSON object with these accepted fields:

| Field | Type | Requirement |
| --- | --- | --- |
| `title` | string | Required; 1–120 characters |
| `completed` | boolean | Optional; defaults to `false` |
| `priority` | string | Optional; one of `low`, `normal`, or `high`; defaults to `normal`. Other values are rejected with `422` |
| `due_date` | string | Optional; ISO calendar date `YYYY-MM-DD`; omitted or `null` means no due date. Invalid dates are rejected with `422` |
| `labels` | array of strings | Optional; defaults to `[]`. At most five labels are allowed; each must contain 1–24 characters after trimming. Labels are trimmed, lowercased, and deduplicated while preserving first-seen order. Invalid values are rejected with `422` |
| `dependency_ids` | array of integers | Optional; defaults to `[]`. Every ID must refer to an existing task, and duplicate IDs are rejected with `422` |

For example:

```json
{
  "title": "Write documentation",
  "completed": false,
  "priority": "normal",
  "due_date": "2026-12-01",
  "labels": ["project", "documentation"],
  "dependency_ids": []
}
```

A successful request returns `201 Created` with the created task, including its generated integer `id`:

```json
{
  "id": 1,
  "title": "Write documentation",
  "completed": false,
  "priority": "normal",
  "due_date": "2026-12-01",
  "due_status": "upcoming",
  "labels": ["project", "documentation"],
  "dependency_ids": []
}
```

Existing request fields and endpoints remain supported. `dependency_ids` is added to task creation and responses, alongside `due_date`, `due_status`, and `labels`; clients should ignore response properties they do not use.

Invalid request data, such as a missing or out-of-range `title`, is rejected with a validation error.

When `completed` is `true`, every listed dependency must already be complete; otherwise the request returns `409 Conflict` without creating the task.

### `POST /tasks/{task_id}/complete`

Marks an existing task complete and returns the task with `200 OK` when it has no dependencies or all its direct dependencies are complete. If any direct dependency is incomplete, the request returns `409 Conflict` and leaves the task unchanged. An unknown task ID returns `404 Not Found`. Completing a task does not complete its dependencies.

Tasks are held in memory and reset when the server restarts. There is no database, authentication, user interface, Copilot customization, or external tool configuration in this starter. Later course modules add capabilities when the exercise requires them.

Run the focused endpoint tests with `python -m unittest discover -s tests`.
