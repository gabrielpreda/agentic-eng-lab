# Capstone feature — review handoff

**Branch:** `capstone/labels`  
**Updated:** 2026-11-18  
**Requirements/spec status:** Implemented from the user request and Miro source  
**Current task:** T-3 complete; all planned tasks T-1–T-3 done

## Implemented criteria

- AC-1–AC-3: optional labels default to `[]`; label lists are validated, normalized, deduplicated in first-seen order, and returned by create/list endpoints.
- AC-4: `GET /tasks?label=value` matches a trimmed, lowercased label exactly, composes with existing filters, returns each task once, and returns `200 []` for no matches.
- AC-5: Existing fields, routes, in-memory storage, and label-omitting requests remain available.

## Deferred or open work

- All related Jira tickets are Done: [BWAA-18](https://build-with-ai.atlassian.net/browse/BWAA-18) (Story), [BWAA-19](https://build-with-ai.atlassian.net/browse/BWAA-19), [BWAA-20](https://build-with-ai.atlassian.net/browse/BWAA-20), and [BWAA-21](https://build-with-ai.atlassian.net/browse/BWAA-21) (Tasks). Their current statuses were verified on 2026-11-18.
- No other work is deferred in the API slice. UI, persistence, authentication, and label mutation remain out of scope.

## Files changed

- `app/main.py`
- `tests/test_api.py`
- `README.md`
- `docs/requirements/capstone-labels.md`
- `docs/specs/capstone-labels.md`
- `docs/tasks/capstone-labels.md`
- `docs/handoffs/capstone-labels.md`

## Verification evidence

| Command/check | Result | Notes |
|---|---|---|
| `.venv/bin/python -m pytest tests/test_api.py -k 'label or defaults_to_incomplete' -q` | Passed: 14 tests | Includes limits, normalization, filtering, and omitted-label compatibility. |
| `.venv/bin/python -m pytest -q` | Passed: 65 tests | Full regression; one existing Starlette/httpx deprecation warning. |

## Review questions and next step

- Review the API and documentation changes on `capstone/labels`; no commit or pull request was created.
- Miro evidence: [tasks/labels](https://miro.com/app/board/uXjVENzs_98=/), diagram widget `3458764690519926990`.
