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
  "priority": "normal"
}
```

The array is empty when there are no tasks. To filter tasks by completion status, use `?completed=true` or `?completed=false`. To filter by priority, use `?priority=low`, `?priority=normal`, or `?priority=high`; other priority values are rejected with `422`. The two filters can be combined (for example `?completed=false&priority=high`), in which case only tasks matching both are returned. Without these query parameters, all tasks are returned. Tasks are always ordered by priority: `high`, then `normal`, then `low`.

### `POST /tasks`

Create a task by sending a JSON object with these accepted fields:

| Field | Type | Requirement |
| --- | --- | --- |
| `title` | string | Required; 1–120 characters |
| `completed` | boolean | Optional; defaults to `false` |
| `priority` | string | Optional; one of `low`, `normal`, or `high`; defaults to `normal`. Other values are rejected with `422` |

For example:

```json
{
  "title": "Write documentation",
  "completed": false,
  "priority": "normal"
}
```

A successful request returns `201 Created` with the created task, including its generated integer `id`:

```json
{
  "id": 1,
  "title": "Write documentation",
  "completed": false,
  "priority": "normal"
}
```

Invalid request data, such as a missing or out-of-range `title`, is rejected with a validation error.

Tasks are held in memory and reset when the server restarts. There is no database, authentication, user interface, Copilot customization, or external tool configuration in this starter. Later course modules add capabilities when the exercise requires them.

Run the focused endpoint tests with `python -m unittest discover -s tests`.
