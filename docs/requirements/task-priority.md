# Task priority — requirements worksheet

**Status:** Approved  
**Approval owner:** Gabriel Preda  
**Last reviewed:** 2026-11-17

## Request

> We need a way for the team to prioritize work. Add priority to tasks so users can see what is urgent. Keep it simple.

Source: [GitHub Issue #6](https://github.com/gabrielpreda/agentic-eng-lab/issues/6).

## User outcome

Users of the Task API can identify urgent work from task priority and retrieve tasks by priority.

## Sources reviewed

| Source | What it establishes | Limits or notes |
|---|---|---|
| [Issue #6](https://github.com/gabrielpreda/agentic-eng-lab/issues/6) | Original request and request to clarify before drafting criteria. | Does not define priority values, API behavior, or ordering. |
| [app/main.py](../../app/main.py#L11-L57) | Current task models, `GET /tasks`, `POST /tasks`, validation, and in-memory storage. | No priority field or update endpoint exists yet. |
| [tests/test_api.py](../../tests/test_api.py) and [tests/test_title_validation.py](../../tests/test_title_validation.py) | Current endpoint, creation, and title-validation coverage. | No priority behavior is covered. |
| [tests/conftest.py](../../tests/conftest.py) and [requirements-test.txt](../../requirements-test.txt) | Tests use a reset in-memory fixture and pytest. | Tests were inspected, not run for this worksheet. |
| [README.md](../../README.md#L20-L76) | Published API contract; tasks are in memory, and the starter has no UI or authentication. | Must be kept in sync if API behavior changes. |
| Repository issue search: [#2](https://github.com/gabrielpreda/agentic-eng-lab/issues/2), [#4](https://github.com/gabrielpreda/agentic-eng-lab/issues/4) | #2 documents the API; #4 covers whitespace-only titles. | Neither is duplicate priority work. Issue search found no other related or duplicate issue. |
| Optional design artifact | None reviewed. | No Miro board was used or changed. |

## Confirmed facts

- The request asks to add task priority so users can see urgency and says to keep the solution simple. (Issue #6)
- The current `TaskCreate` model accepts `title` and `completed`; `Task` adds an integer `id`. `GET /tasks` currently filters by `completed`; `POST /tasks` returns `201`. Tasks are held in memory. ([implementation](../../app/main.py#L11-L57))
- Existing tests cover health, an empty task list, creation defaults and response shape, title rejection, and a created task appearing in the list. The fixture resets stored tasks and IDs. ([tests](../../tests/test_api.py), [title validation](../../tests/test_title_validation.py), [fixture](../../tests/conftest.py))
- Requester clarifications:
  - Allowed priorities are `low`, `normal`, and `high`; omitted priority defaults to `normal`.
  - Priority is optional in the `POST /tasks` request and is always present in successful `POST /tasks` and `GET /tasks` responses.
  - `GET /tasks` filters by one priority using `?priority=<low|normal|high>`.
  - The list is ordered high-first by default; no alternate priority sort is wanted.
  - Priority is set at creation and is not changed afterward.
  - Unsupported priority values are rejected with HTTP 422.

## Assumptions and inferences

| Statement | Evidence | Confirmation needed? |
|---|---|---|
| The existing `completed` filter remains available and can be combined with the new `priority` filter. | It is part of the current `GET /tasks` contract. The requester/trainer requested filter combination, and the requester approved that scope change on 2026-11-17. | No; approved scope-change decision recorded below. |
| Tasks with the same priority may retain their current relative order. | The current list preserves storage order; priority ordering introduces ties. | Yes; see open questions. |
| The README API contract should be updated alongside any implementation. | The README documents current request/response shapes and validation. | Implementation consideration; not a separately confirmed product criterion. |

## Acceptance criteria

**AC-1:** `POST /tasks` accepts an optional `priority` whose value is `low`, `normal`, or `high`. If omitted, the created task has priority `normal`. Unsupported values are rejected with HTTP 422.  
   **Trace:** requester clarifications; existing validation behavior is exercised in [tests/test_api.py](../../tests/test_api.py#L29-L32).
**AC-2:** A successful `POST /tasks` response and every task in a successful `GET /tasks` response include the task's priority.  
   **Trace:** requester clarification; current response models are defined in [app/main.py](../../app/main.py#L11-L27).
**AC-3:** `GET /tasks?priority=<low|normal|high>` returns only tasks with the requested priority. When both `completed` and `priority` filters are supplied, results match both filters. Unsupported priority filter values are rejected with HTTP 422.  
   **Trace:** requester clarification; approved scope change dated 2026-11-17 (requester approval: “Approve the change as requested”); current list filtering is implemented in [app/main.py](../../app/main.py#L42-L49).
**AC-4:** By default, `GET /tasks` orders tasks `high`, then `normal`, then `low`. No alternate priority sort direction is provided.  
   **Trace:** requester clarification; current list behavior is in [app/main.py](../../app/main.py#L42-L49).
**AC-5:** This request does not add behavior for changing a task's priority after creation.  
   **Trace:** requester clarification; the current API has no task-update endpoint ([app/main.py](../../app/main.py#L35-L57)).

## Non-goals and constraints

- No UI, persistence, authentication, or external integration is requested. The starter currently has no UI, authentication, or database ([README](../../README.md#L74)).
- Priority changes after creation and alternate priority sort orders are out of scope, per requester clarification.

## Scope changes

| Date | Change and source | Affected criteria | Approval status |
|---|---|---|---|
| 2026-11-17 | Requester/trainer requested that the existing `completed` filter and new `priority` filter be combinable; requester approved the change with “Approve the change as requested.” | AC-3; the `GET /tasks` contract and filter-combination verification. | Approved for this scope change; the requirements are also approved below. |

## Open questions

- For tasks with equal priority, must their current relative order be preserved, or is their order unspecified? This affects deterministic list-order acceptance and tests.

## Review record

- **Decision:** Requirements approved; the filter-combination scope change is approved, and equal-priority ordering remains open.
- **Reviewed by:** Gabriel Preda.
- **Notes:** Evidence, requester clarifications, the approved scope change, and the requirements approval are recorded above. The equal-priority ordering question remains open.
