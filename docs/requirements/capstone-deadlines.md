# Capstone feature — requirements

**Status:** Approved  
**Source request:** User request in this session  
**Approval owner:** Gabriel Preda

## User outcome

Teams can plan work against dates and quickly identify tasks coming due or already late, while existing clients can continue using the Task API.

## Sources reviewed

| Source | Evidence | Limits or status |
|---|---|---|
| User request | Add due dates, make upcoming and late work easy to see, and keep existing clients working. | Does not define date format or exact API representation. |
| Requester clarifications in this session | Due dates are optional ISO calendar dates; expose computed status and filters; upcoming covers the next 7 days; completed tasks are not overdue; additive response fields are acceptable. | Proposed details remain subject to review with this worksheet. |
| [Current API](../../app/main.py) and [API tests](../../tests/test_api.py) | Tasks are created and listed in memory; list filters include completion and priority; task responses contain `id`, `title`, `completed`, and `priority`. | No due-date behavior exists. |
| [README API contract](../../README.md) | Documents the existing request and response shapes. | Must be updated with the new optional field and response data. |
| [BWAA-16](https://build-with-ai.atlassian.net/browse/BWAA-16) and [BWAA-17](https://build-with-ai.atlassian.net/browse/BWAA-17) | Clarification and implementation tickets for the inclusive due-before-selected-date view. | BWAA-16's confirmed contract is recorded in its Jira comment. |

## Confirmed facts

- The API stores tasks in memory and exposes `POST /tasks` and `GET /tasks`.
- Existing task creation requests may omit the new date.
- Due dates use ISO `YYYY-MM-DD` calendar-date form.
- Response fields may be added while preserving current request fields and endpoint behavior.
- Upcoming means due today through seven calendar days from today, inclusive.
- Completed tasks must not be classified as overdue or upcoming.
- The selected-date view uses `GET /tasks?due_before=YYYY-MM-DD`, includes completed dated tasks by default, excludes tasks without a due date, and composes with existing list filters.

## Assumptions and inferences

- “Keep existing clients working” means keeping current request payloads and endpoint URLs valid and adding response properties; clients must tolerate unknown JSON properties.
- The service's local calendar date is the reference date for computing due status.
- A task due later than the upcoming window is classified as `scheduled`, rather than upcoming.

## Acceptance criteria

1. **AC-1:** `POST /tasks` accepts an optional `due_date` in ISO `YYYY-MM-DD` form. Omission remains valid and is represented as no due date. Invalid date values return HTTP 422. Successful task responses expose `due_date`; requests that omit it remain valid.
2. **AC-2:** Every task response includes a computed `due_status`. A task without a due date is `unscheduled`; a completed task is `completed`; an incomplete task due before today is `overdue`; an incomplete task due today through seven days from today, inclusive, is `upcoming`; and an incomplete task due later is `scheduled`.
3. **AC-3:** `GET /tasks?due_status=upcoming` returns only incomplete tasks due today through seven days from today, inclusive. `GET /tasks?due_status=overdue` returns only incomplete tasks due before today. Unsupported `due_status` values return HTTP 422. The due-status filter can be combined with the existing `completed` and `priority` filters, with all supplied filters applied.
4. **AC-4:** Existing task request fields, response fields, endpoints, and behavior remain available. The new request field is optional. Added response fields are `due_date` and `due_status`; no existing field is removed or renamed.
5. **AC-5:** `GET /tasks?due_before=<YYYY-MM-DD>` returns tasks whose non-null `due_date` is on or before the selected date, including completed tasks by default. Invalid or non-ISO calendar dates return HTTP 422. The filter composes with `completed`, `priority`, and `due_status`.

## Constraints and non-goals

- Preserve the in-memory storage model and existing task API.
- No due-date update route, UI, persistence, authentication, or external integration is requested.
- Date-only semantics are used; no time-of-day or timezone is part of the due date.

## Open questions

- None identified from the request and clarifications above.

## Decisions and scope changes

| Date/source | Decision or change | Approval/status | Affected criteria |
|---|---|---|---|
| 2026-11-17, requester clarification and approval | Use optional ISO calendar dates, a 7-day inclusive upcoming window, exclude completed tasks from upcoming/overdue, expose computed status and filters, and allow additive response properties. | Approved for implementation | AC-1–AC-4 |
| 2026-11-17, requester confirmation for [BWAA-16](https://build-with-ai.atlassian.net/browse/BWAA-16) | Add `GET /tasks?due_before=YYYY-MM-DD`; use an inclusive cutoff, include completed dated tasks by default, exclude unscheduled tasks, reject invalid dates with 422, and compose with existing filters. | Confirmed; recorded on BWAA-16 | AC-5 |
