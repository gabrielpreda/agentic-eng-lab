import pytest


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
    }


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
