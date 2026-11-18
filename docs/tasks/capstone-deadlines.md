# Capstone feature — task plan

**Status:** Approved  
**Requirements:** `docs/requirements/capstone-deadlines.md`  
**Specification:** `docs/specs/capstone-deadlines.md`

| Task ID | Reviewable outcome | Acceptance criteria | Planned verification | Depends on | Status |
|---|---|---|---|---|---|
| T-1 | Accept optional due dates on task creation and include the date in task responses. | AC-1, AC-4 | `.venv/bin/python -m pytest tests/test_api.py -k due_date -q`: 5 passed; `.venv/bin/python -m pytest tests/test_api.py -q`: 39 passed (2026-11-17). | — | Done |
| T-2 | Compute and expose a due status consistently for task responses. | AC-2 | `.venv/bin/python -m pytest tests/test_api.py -k due_status -q`: 1 passed; `.venv/bin/python -m pytest tests/test_api.py -q`: 40 passed (2026-11-17). | T-1 | Done |
| T-3 | Filter task lists by upcoming or overdue status and document the new API contract. | AC-3, AC-4 | `.venv/bin/python -m pytest tests/test_api.py -k due_status -q`: 5 passed; `.venv/bin/python -m pytest -q`: 45 passed (2026-11-17). | T-2 | Done |
| T-4 | Filter tasks due on or before a selected date using the confirmed API contract, preserve filter composition, and document the behavior. | AC-5 | `.venv/bin/python -m pytest tests/test_api.py -k due_before -q`: 7 passed; `.venv/bin/python -m pytest -q`: 52 passed (2026-11-17). | T-3 | Done |

## Traceability

| Acceptance criterion | Task(s) | Test/check | Covered, deferred, or blocked? |
|---|---|---|---|
| AC-1 | T-1 | Valid, missing, and invalid due-date creation tests | Covered |
| AC-2 | T-2 | Status and date-boundary tests | Covered |
| AC-3 | T-3 | Due-status filters, invalid filter, and combined-filter tests | Covered |
| AC-4 | T-1, T-3 | Existing request regression tests, full suite, README/API contract review | Covered |
| AC-5 | T-4 | Inclusive selected-date filter, completed/unscheduled behavior, invalid date, and combined-filter tests | Covered |

## Deferred work

- Due-date updates, UI, persistence, authentication, and external integrations.

## Scope change record

- 2026-11-17: Requester clarified optional ISO calendar dates, computed status and filters, a 7-calendar-day inclusive upcoming window, exclusion of completed tasks from upcoming/overdue, and acceptance of additive response fields.
- 2026-11-17: Requester confirmed the BWAA-16 selected-date contract: `due_before`, inclusive cutoff, include completed dated tasks, exclude undated tasks, reject invalid dates with 422, and compose with existing filters.
