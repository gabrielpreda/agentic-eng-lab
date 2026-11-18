"""Exercise a minimal live HTTP flow against the Task API.

The script launches Uvicorn as a child process on ``127.0.0.1:8000`` and
checks that the service becomes healthy, accepts task creation, and returns
the created task from its list endpoint. It is intended as a CI smoke check,
complementing the in-process API tests with a real HTTP server.

Run this script from the repository root after installing the application
dependencies. The port is fixed, so another service must not already be
listening on port 8000. Task data is held in the child process's in-memory
store and disappears when that process exits. The child server is stopped on
both success and failure.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"


def request_json(path: str, *, method: str = "GET", payload: dict | None = None) -> tuple[int, object]:
    """Send one JSON request to the local API and decode its JSON response.

    ``path`` is appended to ``BASE_URL``; ``method`` defaults to ``GET``.
    When ``payload`` is provided, it is JSON-encoded and sent as the request
    body. Return the HTTP status and decoded response body. Network errors,
    timeouts, and non-success HTTP responses are allowed to propagate to the
    caller.
    """
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=3) as response:
        return response.status, json.load(response)


def wait_until_ready(process: subprocess.Popen[bytes]) -> None:
    """Wait for the child server's health endpoint, or fail on timeout/exit.

    Poll ``/healthz`` for up to 20 seconds, retrying connection and timeout
    errors every half second. Readiness requires both HTTP 200 and the exact
    response ``{"status": "ok"}``. If the server exits before becoming
    ready, raise ``RuntimeError``; if the deadline expires, raise
    ``TimeoutError``.
    """
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Uvicorn exited early with status {process.returncode}")
        try:
            status, body = request_json("/healthz")
        except (URLError, TimeoutError, ConnectionError):
            time.sleep(0.5)
            continue
        if status == 200 and body == {"status": "ok"}:
            return
        time.sleep(0.5)
    raise TimeoutError("Task API did not become ready within 20 seconds")


def main() -> int:
    """Start Uvicorn, exercise the health/create/list flow, and clean up.

    The smoke flow creates a task using only its required title, expects
    ``201`` and the submitted title in the response, then expects ``200`` and
    a list containing the created task's ID. Any unexpected result raises an
    exception and makes the script fail. The server is always terminated in
    ``finally``; if it does not stop within five seconds, it is killed.
    """
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_until_ready(process)

        status, created = request_json(
            "/tasks",
            method="POST",
            payload={"title": "CI smoke task"},
        )
        if status != 201 or not isinstance(created, dict) or created.get("title") != "CI smoke task":
            raise AssertionError(f"Unexpected task creation response: status={status}, body={created!r}")

        status, tasks = request_json("/tasks")
        if status != 200 or not isinstance(tasks, list):
            raise AssertionError(f"Unexpected task list response: status={status}, body={tasks!r}")
        if not any(task.get("id") == created.get("id") for task in tasks if isinstance(task, dict)):
            raise AssertionError("Created task was not present in the subsequent task list")

        print("Live API smoke check passed: health, create task, and list task")
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
