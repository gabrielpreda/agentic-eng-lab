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
        "labels": [],
        "dependency_ids": [],
    }


@pytest.mark.parametrize("dependency_ids", [None, []])
def test_create_task_defaults_to_empty_dependencies(client, dependency_ids):
    task_data = {"title": "Create a task"}
    if dependency_ids is not None:
        task_data["dependency_ids"] = dependency_ids

    created = client.post("/tasks", json=task_data)
    listed = client.get("/tasks")

    assert created.status_code == 201
    assert created.json()["dependency_ids"] == []
    assert listed.status_code == 200
    assert listed.json()[0]["dependency_ids"] == []


def test_create_task_saves_existing_dependency_ids_in_responses(client):
    first = client.post("/tasks", json={"title": "First prerequisite"}).json()
    second = client.post("/tasks", json={"title": "Second prerequisite"}).json()

    created = client.post(
        "/tasks",
        json={
            "title": "Dependent task",
            "dependency_ids": [first["id"], second["id"]],
        },
    )
    listed = client.get("/tasks")

    assert created.status_code == 201
    assert set(created.json()["dependency_ids"]) == {first["id"], second["id"]}
    assert len(created.json()["dependency_ids"]) == 2
    assert listed.status_code == 200
    assert {
        task["id"]: task["dependency_ids"] for task in listed.json()
    } == {
        first["id"]: [],
        second["id"]: [],
        created.json()["id"]: created.json()["dependency_ids"],
    }


def test_create_task_rejects_unknown_dependency_id_without_creating_task(client):
    existing = client.post("/tasks", json={"title": "Existing task"}).json()

    response = client.post(
        "/tasks",
        json={"title": "Dependent task", "dependency_ids": [999]},
    )

    assert response.status_code == 422
    assert [task["id"] for task in client.get("/tasks").json()] == [
        existing["id"]
    ]


def test_create_task_rejects_duplicate_dependency_ids_without_creating_task(
    client,
):
    existing = client.post("/tasks", json={"title": "Existing task"}).json()

    response = client.post(
        "/tasks",
        json={
            "title": "Dependent task",
            "dependency_ids": [existing["id"], existing["id"]],
        },
    )

    assert response.status_code == 422
    assert [task["id"] for task in client.get("/tasks").json()] == [
        existing["id"]
    ]


def test_create_task_rejects_guessed_self_dependency_as_unknown(client):
    first = client.post("/tasks", json={"title": "First task"}).json()

    response = client.post(
        "/tasks",
        json={
            "title": "Self-dependent task",
            "dependency_ids": [first["id"] + 1],
        },
    )

    assert response.status_code == 422
    assert [task["id"] for task in client.get("/tasks").json()] == [first["id"]]


def test_create_task_can_link_dependencies_to_previously_created_task_chain(
    client,
):
    first = client.post("/tasks", json={"title": "First task"}).json()
    second = client.post(
        "/tasks",
        json={"title": "Second task", "dependency_ids": [first["id"]]},
    ).json()

    third_response = client.post(
        "/tasks",
        json={"title": "Third task", "dependency_ids": [second["id"]]},
    )

    assert third_response.status_code == 201
    assert second["dependency_ids"] == [first["id"]]
    assert third_response.json()["dependency_ids"] == [second["id"]]


def test_create_task_normalizes_labels_and_lists_them(client):
    created = client.post(
        "/tasks",
        json={
            "title": "Organize project work",
            "labels": [" Project ", "ops", "project", " Ops "],
        },
    )

    listed = client.get("/tasks")

    assert created.status_code == 201
    assert created.json()["labels"] == ["project", "ops"]
    assert listed.status_code == 200
    assert listed.json()[0]["labels"] == ["project", "ops"]


def test_create_task_accepts_five_labels_and_24_character_labels(client):
    labels = ["a", "b" * 24, "c", "d", "e"]

    response = client.post(
        "/tasks",
        json={"title": "Organize project work", "labels": labels},
    )

    assert response.status_code == 201
    assert response.json()["labels"] == labels


@pytest.mark.parametrize(
    "labels",
    [
        ["one", "two", "three", "four", "five", "six"],
        ["duplicate"] * 6,
        [""],
        ["   "],
        ["x" * 25],
        "project",
        None,
        ["project", 1],
    ],
)
def test_create_task_rejects_invalid_labels(client, labels):
    response = client.post(
        "/tasks",
        json={"title": "Organize project work", "labels": labels},
    )

    assert response.status_code == 422
    assert client.get("/tasks").json() == []


def test_list_tasks_filters_by_normalized_label_once(client):
    client.post(
        "/tasks",
        json={
            "title": "Matching task",
            "labels": [" Project ", "project", "Ops"],
        },
    )
    client.post(
        "/tasks",
        json={"title": "Different label", "labels": ["design"]},
    )
    client.post(
        "/tasks",
        json={"title": "Partial label", "labels": ["project-management"]},
    )

    response = client.get("/tasks", params={"label": " PROJECT "})

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Matching task"]


def test_list_tasks_returns_empty_list_when_label_does_not_match(client):
    client.post(
        "/tasks",
        json={"title": "Project task", "labels": ["project"]},
    )

    response = client.get("/tasks", params={"label": "workstream"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_combines_label_with_existing_filters(client, monkeypatch):
    _freeze_today(monkeypatch)
    tasks = [
        ("matching", False, "high", "2026-12-09", ["project"]),
        ("completed", True, "high", "2026-12-09", ["project"]),
        ("wrong priority", False, "normal", "2026-12-09", ["project"]),
        ("wrong label", False, "high", "2026-12-09", ["design"]),
        ("after cutoff", False, "high", "2026-12-11", ["project"]),
        ("not overdue", False, "high", "2026-12-10", ["project"]),
    ]
    for title, completed, priority, due_date, labels in tasks:
        client.post(
            "/tasks",
            json={
                "title": title,
                "completed": completed,
                "priority": priority,
                "due_date": due_date,
                "labels": labels,
            },
        )

    response = client.get(
        "/tasks",
        params={
            "label": " PROJECT ",
            "completed": False,
            "priority": "high",
            "due_status": "overdue",
            "due_before": "2026-12-10",
        },
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["matching"]


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
