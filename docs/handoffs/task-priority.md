# Task priority — implementation handoff

Update this note from the current repository state before changing to a new Copilot session. Keep it concise and factual.

**Updated:** 2026-11-18  
**Requirements status:** Approved; see `docs/requirements/task-priority.md`  
**Specification status:** Approved; see `docs/specs/task-priority.md`  
**Current task:** T-4 complete; all planned tasks T-1–T-4 done  
**Task status:** T-1 Done; T-2 Done; T-3 Done; T-4 Done  
**Acceptance criteria:** AC-4 and AC-5 for T-4 (AC-1 by T-1, AC-2 by T-2, AC-3 by T-3)

## Current state

- **Verified checkout:** `develop` at `c1910b7`. `app/main.py`, `README.md`, and `tests/test_api.py` have no tracked worktree changes. The worktree has unrelated untracked `.github/pull_request_template.md`, `Dockerfile`, and `docs/handoffs/capstone-verification-template.md`.
- The priority implementation is part of repository history, not an uncommitted change. The four `capstone/*` feature commits are also present in the merged `main` history.
- **Decision(s):** Requirements, specification, and task list are approved. Combining `completed` and `priority` filters is approved and implemented. Ordering uses a stable sort, so equal-priority tasks keep stored order, but that tie behavior is deliberately not asserted.
- **Unresolved questions/blockers:** Equal-priority ordering is still an open decision in the requirements. No blockers.
- **Current API surface:** `GET /healthz`, `GET /tasks`, `POST /tasks`, and `POST /tasks/{task_id}/complete`; there is no alternate sort parameter or priority-update route.

## Verification evidence

| Command or check | Result | Notes |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_api.py -k "orders or keeps_priority" -q` | Passed: 2 passed | T-4 (AC-4); both tests failed before the change |
| `.venv/bin/python -m pytest -q` | Passed: 35 passed | Full regression after T-4 |
| `.venv/bin/python -m pytest -q` | Passed: 79 passed | Re-run on the verified `develop` checkout (2026-11-18); one existing Starlette/httpx deprecation warning |

## Next step

No T-1–T-4 implementation work remains. The equal-priority ordering question is still open; resolve it before adding a tie-order assertion. Broader feature candidates and team practices are recorded in [the capstone retrospective](../capstone-retrospective.md); they are proposals, not approved implementation scope. No implementation or release authorization is implied.

## Session handoff prompt

Before continuing in a new session, reread the requirements, specification, task list, this handoff, and current diff. Treat the repository artifacts as authoritative rather than relying on the previous chat transcript.
