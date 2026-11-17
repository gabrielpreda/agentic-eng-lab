# Task priority — feature specification

**Status:** Approved  
**Requirements source:** [docs/requirements/task-priority.md](../requirements/task-priority.md)  
**Approval owner:** Gabriel Preda

## Outcome

Task API users can recognize urgency from each task's priority and retrieve tasks of a requested priority. The API continues to support its existing task-creation and completion-filter behavior.

## Current API behavior

- `GET /tasks` returns task objects with `id`, `title`, and `completed`; it can filter by `completed=true|false`, or return all tasks when omitted. ([implementation](../../app/main.py#L42-L49), [README contract](../../README.md#L28-L43))
- `POST /tasks` requires a non-whitespace title of 1–120 characters, optionally accepts `completed` (default `false`), and returns `201` with the created task. Invalid request data returns `422`; tasks are held in memory. ([implementation](../../app/main.py#L11-L57), [README contract](../../README.md#L45-L76))
- The API has no priority field, priority filter, or task-update endpoint today. The existing tests cover task creation and listing, but not priority behavior. ([tests](../../tests/test_api.py), [implementation](../../app/main.py#L11-L57))

## Scope and behavior

| Spec ID | Behavior or constraint | Source criterion |
|---|---|---|
| S-1 | Task creation accepts `low`, `normal`, or `high` priority; omission means `normal`, and unsupported values return `422`. | [AC-1](../requirements/task-priority.md#acceptance-criteria) |
| S-2 | Successful task-creation and task-list responses include priority on every task. | [AC-2](../requirements/task-priority.md#acceptance-criteria) |
| S-3 | A priority query returns only tasks with that priority; unsupported filter values return `422`. When `completed` and `priority` are both supplied, results match both filters. | [AC-3](../requirements/task-priority.md#acceptance-criteria) |
| S-4 | Without another sort option, task lists order priorities `high`, `normal`, then `low`. Equal-priority ordering is unresolved. | [AC-4](../requirements/task-priority.md#acceptance-criteria) |
| S-5 | This scope adds no behavior for changing priority after creation. | [AC-5](../requirements/task-priority.md#acceptance-criteria) |

## Out of scope

- Changing priority after task creation or offering an alternate priority sort order. ([AC-4](../requirements/task-priority.md#acceptance-criteria), [AC-5](../requirements/task-priority.md#acceptance-criteria))
- UI, persistence, authentication, and external integrations. ([requirements constraints](../requirements/task-priority.md#non-goals-and-constraints))

## Verification intent

Add focused API tests for accepted priority values and the default, priority in both response shapes, priority filtering and invalid values, and high-first ordering. Verify that combined `completed` and `priority` filters return only tasks matching both. Equal-priority ordering remains unresolved. Existing tests remain evidence for the current task behavior; they do not yet verify priority.

| Spec ID | Planned evidence | Evidence status |
|---|---|---|
| S-1 | Creation tests for each allowed value, omitted priority, and unsupported values returning `422`. | Planned |
| S-2 | Assertions that successful creation and listing responses include priority. | Planned |
| S-3 | List-filter tests for each allowed priority and unsupported values returning `422`, plus a combined-filter test asserting that only tasks matching both `completed` and `priority` are returned. | Planned |
| S-4 | List-order test covering `high`, `normal`, and `low`; tie behavior awaits decision. | Planned |
| S-5 | Review the API surface to confirm no priority-change behavior is added. | Planned |

## Assumptions and unresolved decisions

- Preserve the existing `completed` filter and combine it with `priority` when both are supplied, as approved in [AC-3](../requirements/task-priority.md#acceptance-criteria).
- Equal-priority tasks may preserve their current relative order or have unspecified order; the requirements do not decide which. Resolve before asserting tie behavior.
- The requirements and specification are Approved by Gabriel Preda. Implementation remains gated on selection of a task.

## Scope changes

| Date | Change and source | Affected criteria/tasks/evidence | Review status |
|---|---|---|---|
| 2026-11-17 | Requester/trainer requested that the existing `completed` filter and the new `priority` filter be combinable; requester approved the change with “Approve the change as requested.” | AC-3 / S-3; T-3; verify that supplying both filters returns only tasks matching both. | Approved for this scope change; requirements and specification are also approved. |

### Approved scope change: combine task-list filters

The approved behavior is that a single `GET /tasks` request may supply both `completed` and `priority`, and the returned tasks must satisfy both filters. The requirements' AC-3 was updated first to record this decision. The separate equal-priority ordering question remains open.
