# Capstone feature — review handoff

**Branch:** `capstone/deadlines`  
**Updated:** 2026-11-17  
**Requirements/spec status:** Approved  
**Current task:** T-4 complete; all planned tasks T-1–T-4 done

## Implemented criteria

- **AC-1:** `POST /tasks` accepts optional ISO `YYYY-MM-DD` dates; invalid dates return 422 and omitted dates remain valid.
- **AC-2:** Task responses include `due_date` and computed `due_status`: `unscheduled`, `completed`, `overdue`, `upcoming`, or `scheduled`.
- **AC-3:** `GET /tasks?due_status=upcoming|overdue` filters incomplete tasks; it composes with the existing `completed` and `priority` filters.
- **AC-4:** Existing endpoints and request fields remain available; the README documents the additive response fields.
- **AC-5:** `GET /tasks?due_before=YYYY-MM-DD` includes dated tasks due on or before the selected date, includes completed tasks by default, excludes unscheduled tasks, rejects invalid dates with 422, and composes with existing filters.

## Deferred or open work

- No open questions or blockers.
- The selected-date contract was confirmed in BWAA-16 and recorded there; BWAA-16 is Done. BWAA-17 implementation and verification are complete.
- The Miro board could not be read because the Miro MCP connection required OAuth. The selected-date contract was taken from BWAA-16 and explicitly confirmed by the requester.
- Due-date updates, UI, persistence, authentication, and external integrations remain out of scope.

## Files changed

- `app/main.py`
- `tests/test_api.py`
- `README.md`
- `docs/requirements/capstone-deadlines.md`
- `docs/specs/capstone-deadlines.md`
- `docs/tasks/capstone-deadlines.md`
- `docs/handoffs/capstone-deadlines.md`

## Verification evidence

| Command/check | Result | Notes |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_api.py -k due_before -q` | Passed: 7 passed | Inclusive cutoff, completed and unscheduled tasks, invalid dates, and combined filters |
| `.venv/bin/python -m pytest tests/test_api.py -k 'due_before or due_date or due_status' -q` | Passed: 17 passed | Selected-date and existing due-date/status regression |
| `.venv/bin/python -m pytest -q` | Passed: 52 passed | Full regression; one existing Starlette `httpx` deprecation warning |

## Review questions and next step

- No implementation work remains in the approved task plan. Review the changes and decide whether to commit; nothing has been committed.
