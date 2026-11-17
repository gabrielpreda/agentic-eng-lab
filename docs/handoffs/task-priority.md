# Task priority — implementation handoff

Update this note from the current repository state before changing to a new Copilot session. Keep it concise and factual.

**Updated:** 2026-11-17  
**Requirements status:** Approved; see `docs/requirements/task-priority.md`  
**Specification status:** Approved; see `docs/specs/task-priority.md`  
**Current task:** T-4 complete; all planned tasks T-1–T-4 done  
**Task status:** T-1 Done; T-2 Done; T-3 Done; T-4 Done  
**Acceptance criteria:** AC-4 and AC-5 for T-4 (AC-1 by T-1, AC-2 by T-2, AC-3 by T-3)

## Current state

- **Implementation files currently modified in the worktree:** `app/main.py`, `README.md`, and `tests/test_api.py` contain the priority implementation along with the later deadline feature. This handoff is being updated to correct its previous file-state note; `docs/tasks/task-priority.md` is not currently modified.
- **Decision(s):** Requirements, specification, and task list are approved. Combining `completed` and `priority` filters is approved and implemented. Ordering uses a stable sort, so equal-priority tasks keep stored order, but that tie behavior is deliberately not asserted.
- **Unresolved questions/blockers:** Equal-priority ordering is still an open decision in the requirements. No blockers.
- **API-surface review (AC-5):** Only `GET /healthz`, `GET /tasks`, `POST /tasks`; no sort parameter and no priority-update route.

## Verification evidence

| Command or check | Result | Notes |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_api.py -k "orders or keeps_priority" -q` | Passed: 2 passed | T-4 (AC-4); both tests failed before the change |
| `.venv/bin/python -m pytest -q` | Passed: 35 passed | Full regression after T-4 |
| `.venv/bin/python -m pytest -q` | Passed: 52 passed | Latest full regression, including the selected-date deadline tickets (2026-11-17) |

## Next step

Nothing is planned. Remaining work is outside the task list: resolve the equal-priority ordering question (and add a tie test if the answer is "preserve order"), then review the diff and decide on committing. Nothing has been committed.

## Session handoff prompt

Before continuing in a new session, reread the requirements, specification, task list, this handoff, and current diff. Treat the repository artifacts as authoritative rather than relying on the previous chat transcript.
