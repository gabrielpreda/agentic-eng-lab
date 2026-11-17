# Task priority — implementation task list

**Status:** Approved  
**Approval owner:** Gabriel Preda  
**Specification:** `docs/specs/task-priority.md`  
**Requirements:** `docs/requirements/task-priority.md`

| Task ID | Reviewable result | Acceptance criteria | Planned verification evidence | Depends on | Status |
|---|---|---|---|---|---|
| T-1 | Task creation accepts `low`, `normal`, or `high`, defaults omitted priority to `normal`, and rejects unsupported values with HTTP 422. | AC-1 | Planned focused API tests for each allowed value, the omitted-value default, and an unsupported value returning 422. | — | Done — `.venv/bin/python -m pytest tests/test_api.py -k priority -v`: 9 passed; `.venv/bin/python -m pytest -q`: 16 passed (2026-11-17) |
| T-2 | Successful task-creation and task-list responses include each task's priority. | AC-2 | Planned focused API assertions on the priority field and value in both response shapes. | T-1 | Done — `.venv/bin/python -m pytest tests/test_api.py -k priority -v`: 12 passed; `.venv/bin/python -m pytest -q`: 19 passed (2026-11-17). No app code change; behavior was already provided by T-1. |
| T-3 | The task list supports priority filtering and can combine it with the existing `completed` filter; unsupported priority filters return HTTP 422. | AC-3 | Planned focused API tests for each supported priority filter, an unsupported value returning 422, and a request supplying both filters that asserts only tasks matching both are returned. Include a regression check for the existing `completed` filter. | T-1 | Done — `.venv/bin/python -m pytest tests/test_api.py -k filter -q`: 14 passed; `.venv/bin/python -m pytest -q`: 33 passed (2026-11-17). Tests written first: 12 new tests failed before the change; the 2 `completed`-only regression tests already passed. |
| T-4 | Task lists order priorities `high`, `normal`, then `low`, with no alternate priority sort or priority-change behavior added. | AC-4, AC-5 | Planned focused API ordering test across all three priorities and an API-surface review for alternate sorting or priority mutation behavior. | T-1 | Done — `.venv/bin/python -m pytest tests/test_api.py -k "orders or keeps_priority" -q`: 2 passed (both failed before the change); `.venv/bin/python -m pytest -q`: 35 passed (2026-11-17). API-surface review: only `GET /healthz`, `GET /tasks`, `POST /tasks`; no sort parameter or priority-update route. Tie order is not asserted (stable sort keeps stored order; decision still open). |

## Traceability check

| Acceptance criterion | Task IDs | Planned verification evidence | Coverage |
|---|---|---|---|
| AC-1 | T-1 | Allowed-value, default, and invalid-creation API tests | Covered |
| AC-2 | T-2 | Creation and list response-shape API assertions | Covered |
| AC-3 | T-3 | Priority-filter and invalid-filter API tests; existing `completed` filter regression check; combined-filter API test asserting both conditions apply | Covered by planned verification |
| AC-4 | T-4 | API ordering test for `high`, `normal`, and `low` | Covered for priority order; tie order awaits decision |
| AC-5 | T-4 | Review the API surface for absence of priority mutation behavior | Covered |

## Open decisions

- Whether tasks with equal priority preserve their current relative order or have unspecified order. Until resolved, T-4 verifies only ordering between priority groups.

## Unrelated tasks

None. Each task advances one or more listed acceptance criteria.

## Scope changes

Keep this aligned with the scope-change record in `docs/specs/task-priority.md`.

| Date | Change and source | Affected criteria/tasks/planned verification | Review status |
|---|---|---|---|
| 2026-11-17 | Requester/trainer requested that `completed` and `priority` filters be combinable; requester approved the change with “Approve the change as requested.” | AC-3 / T-3; planned API test supplying both filters and asserting only tasks matching both are returned. Existing independent-filter and invalid-priority checks remain. | Approved for this scope change; requirements and specification are also approved. |

The requirements, specification, and task list are approved by Gabriel Preda. T-1, T-2, T-3, and T-4 are Done (evidence above). The equal-priority ordering decision remains open.
