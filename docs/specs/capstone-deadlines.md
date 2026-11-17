# Capstone feature — specification

**Status:** Approved  
**Requirements:** `docs/requirements/capstone-deadlines.md`  
**Approval owner:** Gabriel Preda

## Outcome and scope

Task API clients can create tasks with optional calendar due dates, see their computed due status, and filter for upcoming or overdue work. Existing routes and request fields continue to work; task responses add `due_date` and `due_status`.

## Behavior and constraints

| Spec ID | Observable behavior or constraint | Source AC |
|---|---|---|
| S-1 | `POST /tasks` accepts optional ISO `YYYY-MM-DD` `due_date`; omitted dates remain valid, and invalid dates return 422. | AC-1 |
| S-2 | Task responses include `due_date` and a computed `due_status`: `unscheduled`, `completed`, `overdue`, `upcoming`, or `scheduled`, according to the requirements' calendar-date boundaries. | AC-2 |
| S-3 | `GET /tasks?due_status=upcoming` and `?due_status=overdue` filter to the corresponding incomplete tasks. Unsupported values return 422. The filter composes with `completed` and `priority`. | AC-3 |
| S-4 | Keep existing endpoints, request fields, response fields, and behavior; add only optional request and response properties. | AC-4 |
| S-5 | `GET /tasks?due_before=YYYY-MM-DD` includes tasks with a non-null due date on or before the cutoff; completed tasks are included unless narrowed by `completed`. Invalid dates return 422. The filter composes with `completed`, `priority`, and `due_status`. | AC-5 |

## Exclusions and deferred work

- Updating a due date after creation.
- UI, persistence, authentication, and external integrations.
- Time-of-day and timezone semantics.

## Verification intent

| Spec ID | Planned test/check | Status |
|---|---|---|
| S-1 | Creation accepts a valid date, defaults an omitted date, rejects malformed dates with 422, and preserves existing request payload behavior. | Verified by T-1 and the full suite (52 passed, 2026-11-17) |
| S-2 | Cover each status and date boundaries (before today, today, seven days, and after seven days), including completed tasks and tasks without dates. | Verified by T-2 and the full suite (52 passed, 2026-11-17) |
| S-3 | Verify upcoming/overdue filters, invalid filter rejection, and combination with existing filters. | Verified by T-3 and the full suite (52 passed, 2026-11-17) |
| S-4 | Run the complete test suite and review the README/API response contract for backward-compatible additions. | Verified; README updated and full suite passed (52 passed, 2026-11-17) |
| S-5 | Verify inclusive cutoff, exclusion of unscheduled tasks, completed-task inclusion, invalid dates, and combination with all existing filters. | Verified: `pytest tests/test_api.py -k due_before -q` (7 passed) |

## Assumptions and unresolved decisions

- The current local calendar date is used as “today.”
- Upcoming includes tasks due today and through the seventh following calendar day.
- Completed tasks receive status `completed` regardless of due date and do not match upcoming or overdue filters.
- A task more than seven days from its due date is `scheduled`.
- `due_before` includes completed tasks with a date on or before its cutoff; tasks without dates cannot match.

## Change record

| Date/source | Change | Affected ACs/tasks/checks | Approval status |
|---|---|---|---|
| 2026-11-17, requester clarification and approval | Specified optional calendar dates, computed due status, upcoming/overdue filters, and additive response fields. | AC-1–AC-4; T-1–T-3 | Approved for implementation |
| 2026-11-17, requester confirmation for [BWAA-16](https://build-with-ai.atlassian.net/browse/BWAA-16) | Specified the `due_before` query parameter, inclusive cutoff, completed/unscheduled behavior, 422 validation, and filter composition. | AC-5; T-4; S-5 verification | Approved |
