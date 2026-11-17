from datetime import date, timedelta

import pytest

import app.main as task_api


class FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 12, 10)


def _freeze_today(monkeypatch):
    monkeypatch.setattr(task_api, "date", FixedDate)


def test_healthz_reports_service_is_running(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks_starts_empty(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_create_task_defaults_to_incomplete(client):
    response = client.post("/tasks", json={"title": "Write API docs"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Write API docs",
        "completed": False,
        "priority": "normal",
        "due_date": None,
        "due_status": "unscheduled",
    }


def test_task_responses_include_computed_due_status(client, monkeypatch):
    _freeze_today(monkeypatch)
    today = date(2026, 12, 10)
    cases = [
        ("No date", {}, "unscheduled"),
        (
            "Completed late",
            {"completed": True, "due_date": (today - timedelta(days=1)).isoformat()},
            "completed",
        ),
        (
            "Overdue",
            {"due_date": (today - timedelta(days=1)).isoformat()},
            "overdue",
        ),
        ("Due today", {"due_date": today.isoformat()}, "upcoming"),
        (
            "Due in seven days",
            {"due_date": (today + timedelta(days=7)).isoformat()},
            "upcoming",
        ),
        (
            "Due in eight days",
            {"due_date": (today + timedelta(days=8)).isoformat()},
            "scheduled",
        ),
    ]

    results = []
    for title, fields, _ in cases:
        response = client.post("/tasks", json={"title": title, **fields})
        assert response.status_code == 201
        results.append(response.json())

    assert [task["due_status"] for task in results] == [
        expected_status for _, _, expected_status in cases
    ]
    listed = client.get("/tasks")
    assert [task["due_status"] for task in listed.json()] == [
        expected_status for _, _, expected_status in cases
    ]


def test_create_task_accepts_due_date_and_lists_it(client):
    created = client.post(
        "/tasks",
        json={"title": "Plan the release", "due_date": "2026-12-01"},
    )

    listed = client.get("/tasks")

    assert created.status_code == 201
    assert created.json()["due_date"] == "2026-12-01"
    assert listed.status_code == 200
    assert listed.json()[0]["due_date"] == "2026-12-01"


def test_create_task_defaults_due_date_to_none(client):
    created = client.post("/tasks", json={"title": "No deadline yet"})
    explicitly_empty = client.post(
        "/tasks",
        json={"title": "Still no deadline", "due_date": None},
    )

    assert created.status_code == 201
    assert created.json()["due_date"] is None
    assert explicitly_empty.status_code == 201
    assert explicitly_empty.json()["due_date"] is None


@pytest.mark.parametrize(
    "due_date",
    ["not-a-date", "2026-02-30", "2026-12-01T12:00:00"],
)
def test_create_task_rejects_invalid_due_date(client, due_date):
    response = client.post(
        "/tasks",
        json={"title": "Plan the release", "due_date": due_date},
    )

    assert response.status_code == 422
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize("title", ["", " \t\n"])
def test_create_task_rejects_empty_or_whitespace_title(client, title):
    response = client.post("/tasks", json={"title": title})

    assert response.status_code == 422


@pytest.mark.parametrize("priority", ["low", "normal", "high"])
def test_create_task_accepts_supported_priority(client, priority):
    response = client.post(
        "/tasks",
        json={"title": "Prioritize work", "priority": priority},
    )

    assert response.status_code == 201
    assert response.json()["priority"] == priority


def test_create_task_defaults_priority_to_normal(client):
    response = client.post("/tasks", json={"title": "Prioritize work"})

    assert response.status_code == 201
    assert response.json()["priority"] == "normal"


@pytest.mark.parametrize("priority", ["urgent", "HIGH", "", None, 1])
def test_create_task_rejects_unsupported_priority(client, priority):
    response = client.post(
        "/tasks",
        json={"title": "Prioritize work", "priority": priority},
    )

    assert response.status_code == 422
    assert client.get("/tasks").json() == []


@pytest.mark.parametrize("priority", ["low", "normal", "high"])
def test_task_list_includes_priority_for_every_task(client, priority):
    created = client.post(
        "/tasks",
        json={"title": "Prioritize work", "priority": priority},
    )

    listed = client.get("/tasks")

    assert created.json()["priority"] == priority
    assert listed.status_code == 200
    assert [task["priority"] for task in listed.json()] == [priority]


def test_created_task_appears_in_list(client):
    created = client.post(
        "/tasks",
        json={"title": "Review test feedback", "completed": True},
    )

    listed = client.get("/tasks")

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json() == [created.json()]


def _seed_tasks(client):
    for title, completed, priority in [
        ("low open", False, "low"),
        ("low done", True, "low"),
        ("normal open", False, "normal"),
        ("normal done", True, "normal"),
        ("high open", False, "high"),
        ("high done", True, "high"),
    ]:
        client.post(
            "/tasks",
            json={"title": title, "completed": completed, "priority": priority},
        )


@pytest.mark.parametrize("priority", ["low", "normal", "high"])
def test_list_tasks_filters_by_priority(client, priority):
    _seed_tasks(client)

    response = client.get("/tasks", params={"priority": priority})

    assert response.status_code == 200
    titles = {task["title"] for task in response.json()}
    assert titles == {f"{priority} open", f"{priority} done"}
    assert all(task["priority"] == priority for task in response.json())


def test_list_tasks_filters_by_due_status_and_combines_filters(client, monkeypatch):
    _freeze_today(monkeypatch)
    today = date(2026, 12, 10)
    tasks = [
        ("today high", today, False, "high"),
        ("seven days normal", today + timedelta(days=7), False, "normal"),
        ("completed today", today, True, "high"),
        ("late high", today - timedelta(days=1), False, "high"),
        ("completed late", today - timedelta(days=1), True, "high"),
        ("later high", today + timedelta(days=8), False, "high"),
    ]
    for title, due_date, completed, priority in tasks:
        client.post(
            "/tasks",
            json={
                "title": title,
                "due_date": due_date.isoformat(),
                "completed": completed,
                "priority": priority,
            },
        )

    upcoming = client.get("/tasks", params={"due_status": "upcoming"})
    overdue = client.get("/tasks", params={"due_status": "overdue"})
    combined = client.get(
        "/tasks",
        params={
            "due_status": "upcoming",
            "completed": False,
            "priority": "high",
        },
    )

    assert {task["title"] for task in upcoming.json()} == {
        "today high",
        "seven days normal",
    }
    assert [task["title"] for task in overdue.json()] == ["late high"]
    assert [task["title"] for task in combined.json()] == ["today high"]


def test_list_tasks_filters_by_due_before_inclusively(client):
    tasks = [
        ("due before", "2026-12-09", False),
        ("due on selected date", "2026-12-10", True),
        ("due after", "2026-12-11", False),
        ("unscheduled", None, False),
    ]
    for title, due_date, completed in tasks:
        client.post(
            "/tasks",
            json={"title": title, "due_date": due_date, "completed": completed},
        )

    response = client.get("/tasks", params={"due_before": "2026-12-10"})

    assert response.status_code == 200
    assert {task["title"] for task in response.json()} == {
        "due before",
        "due on selected date",
    }


def test_list_tasks_combines_due_before_with_existing_filters(client, monkeypatch):
    _freeze_today(monkeypatch)
    tasks = [
        ("matching", "2026-12-09", False, "high"),
        ("completed", "2026-12-08", True, "high"),
        ("wrong priority", "2026-12-09", False, "normal"),
        ("after selected date", "2026-12-11", False, "high"),
        ("no due date", None, False, "high"),
    ]
    for title, due_date, completed, priority in tasks:
        client.post(
            "/tasks",
            json={
                "title": title,
                "due_date": due_date,
                "completed": completed,
                "priority": priority,
            },
        )

    response = client.get(
        "/tasks",
        params={
            "due_before": "2026-12-10",
            "completed": False,
            "priority": "high",
            "due_status": "overdue",
        },
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["matching"]


@pytest.mark.parametrize(
    "due_before",
    ["not-a-date", "2026-02-30", "2026-12-10T12:00:00", "20261210", ""],
)
def test_list_tasks_rejects_invalid_due_before_filter(client, due_before):
    response = client.get("/tasks", params={"due_before": due_before})

    assert response.status_code == 422


@pytest.mark.parametrize("due_status", ["scheduled", "unknown", ""])
def test_list_tasks_rejects_unsupported_due_status_filter(client, due_status):
    response = client.get("/tasks", params={"due_status": due_status})

    assert response.status_code == 422


@pytest.mark.parametrize("priority", ["urgent", "HIGH", ""])
def test_list_tasks_rejects_unsupported_priority_filter(client, priority):
    _seed_tasks(client)

    response = client.get("/tasks", params={"priority": priority})

    assert response.status_code == 422


@pytest.mark.parametrize("completed", [True, False])
@pytest.mark.parametrize("priority", ["low", "normal", "high"])
def test_list_tasks_combines_completed_and_priority_filters(
    client, completed, priority
):
    _seed_tasks(client)

    response = client.get(
        "/tasks", params={"completed": completed, "priority": priority}
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == [
        f"{priority} {'done' if completed else 'open'}"
    ]


@pytest.mark.parametrize("completed", [True, False])
def test_list_tasks_completed_filter_still_works_alone(client, completed):
    _seed_tasks(client)

    response = client.get("/tasks", params={"completed": completed})

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all(task["completed"] is completed for task in response.json())


def test_list_tasks_orders_high_then_normal_then_low(client):
    for title, priority in [
        ("low first", "low"),
        ("normal second", "normal"),
        ("high third", "high"),
    ]:
        client.post("/tasks", json={"title": title, "priority": priority})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert [task["priority"] for task in response.json()] == [
        "high",
        "normal",
        "low",
    ]


def test_filtered_list_keeps_priority_order(client):
    _seed_tasks(client)

    response = client.get("/tasks", params={"completed": True})

    assert [task["priority"] for task in response.json()] == [
        "high",
        "normal",
        "low",
    ]
