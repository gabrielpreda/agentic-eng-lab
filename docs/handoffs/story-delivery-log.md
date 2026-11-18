# Story delivery log

## Source and scope

- Miro board/frame: [Course task dependencies and completion flow](https://miro.com/app/board/uXjVEM7aIA4=/?moveToWidget=3458764690824328814), CREATE and COMPLETE.
- Miro decisions accepted by: Final user-approved Jira criteria; BWAA-22 blocks BWAA-23.
- Open questions / excluded proposals: None unresolved. BWAA-23 excludes starting or reopening tasks, dependency editing, deletion, and recursive cascade.
- Requirements/spec version: Live Jira descriptions for [BWAA-22](https://build-with-ai.atlassian.net/browse/BWAA-22) and [BWAA-23](https://build-with-ai.atlassian.net/browse/BWAA-23); no separate versioned spec.
- Jira project: BWAA.
- Agreed base branch: `main`; BWAA-23 started from merged `origin/main` at `005ff1f`.

## Story sequence

| Order | Jira key/title | Acceptance criteria | Miro/spec/evidence | Depends on | Status |
|---|---|---|---|---|---|
| 1 | [BWAA-22 — Link prerequisite tasks when creating a task](https://build-with-ai.atlassian.net/browse/BWAA-22) | Accept `dependency_ids` referencing existing tasks; reject unknown or duplicate IDs with 422. | Miro CREATE flow; live Jira criteria. | None | Done |
| 2 | [BWAA-23 — Block task completion while prerequisites remain incomplete](https://build-with-ai.atlassian.net/browse/BWAA-23) | Add completion endpoint; return 200 when direct prerequisites are complete, 409 when any are incomplete, 404 for unknown tasks; reject completed-at-creation with incomplete prerequisites. No cascade. | Miro COMPLETE H–K; live Jira criteria. | BWAA-22 | Done |

## Per-story implementation evidence

### [BWAA-22](https://build-with-ai.atlassian.net/browse/BWAA-22) — Link prerequisite tasks when creating a task

- Live Jira story read at: 2026-11-18; status reverified Done during BWAA-23 closeout.
- Branch/base: `capstone/dependencies` → `main`.
- Existing behavior/regression tests: 11 existing-behavior checks passed before implementation.
- Changed files: `app/main.py`, `tests/test_api.py`, `README.md`.
- Commit: `0e56b0ece66aed72323e464c7c8693a9cca3fe53` (`BWAA-22 add prerequisite task links`).
- Focused test command/result: Exact command was not retained in the available handoff; focused story and preservation tests reported 18 passed.
- Regression test command/result: Initial existing-behavior checks reported 11 passed; exact command was not retained.
- Review findings/fixes: Final dependency direction confirmed as BWAA-22 blocks BWAA-23. Full suite passed (72); `git diff --check` passed.
- Remote push confirmation: `origin/capstone/dependencies` contains the commit.
- CI/PR status (if available): [PR #15](https://github.com/gabrielpreda/agentic-eng-lab/pull/15) merged; no GitHub Actions workflows or PR check runs were available.
- Remaining issues or decisions: None.
- Next story may start? Why/base: Yes; BWAA-23 proceeded from the merged `origin/main`.

### [BWAA-23](https://build-with-ai.atlassian.net/browse/BWAA-23) — Block task completion while prerequisites remain incomplete

- Live Jira story read at: 2026-11-18; status reverified Done after merge.
- Branch/base: `capstone/task-completion-guard`, from `origin/main` at `005ff1f`; merged to `main`.
- Existing behavior/regression tests: Pre-implementation focused regressions passed (22); post-change focused acceptance/regression tests passed (11).
- Changed files: `app/main.py`, `tests/test_api.py`, `README.md`.
- Commit: `ae806eb74edcc307b1ebd5054492d0fb473f6e93` (`BWAA-23 gate task completion on prerequisites`).
- Focused test command/result: `.venv/bin/python -m pytest tests/test_api.py -k 'complete_task or create_completed_task or create_task_defaults_to_incomplete or created_task_appears_in_list or list_tasks_filters_by_due_status_and_combines_filters or list_tasks_filters_by_due_before_inclusively' -q` — 11 passed.
- Regression test command/result: `.venv/bin/python -m pytest tests/test_api.py -k 'create_task_defaults_to_incomplete or created_task_appears_in_list or list_tasks_completed_filter_still_works_alone or list_tasks_combines_completed_and_priority_filters or due_status or due_before' -q` — 22 passed before implementation.
- Review findings/fixes: Full suite `.venv/bin/python -m pytest -q` — 79 passed; `git diff --check` passed. One existing Starlette/httpx deprecation warning.
- Remote push confirmation: `origin/capstone/task-completion-guard` verified at `ae806eb74edcc307b1ebd5054492d0fb473f6e93`.
- CI/PR status (if available): [PR #16](https://github.com/gabrielpreda/agentic-eng-lab/pull/16) merged to `main` at `09a4088966958be8d285ce7b5b2f9747f5ca7a78`. GitHub reported zero Actions workflows, workflow runs, check runs, or commit statuses.
- Remaining issues or decisions: None; no CI workflows are configured.
- Next story may start? Why/base: Both stories are Done. Use the current merged `origin/main` as the base for any separately approved next story.
