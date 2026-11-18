# Task labels — implementation task list

**Status:** Complete  
**Requirements:** `docs/requirements/capstone-labels.md`  
**Specification:** `docs/specs/capstone-labels.md`

| Task ID | Reviewable outcome | Acceptance criteria | Verification | Depends on | Status |
|---|---|---|---|---|---|
| T-1 | Accept optional labels, validate limits, normalize values, and expose labels in task responses. | AC-1, AC-2, AC-3, AC-5 | Label creation, invalid input, response shape, and omitted-label compatibility tests. | — | Done |
| T-2 | Filter tasks by one normalized label and compose that filter with existing task filters. | AC-4, AC-5 | Normalized exact-match, no-match, once-only, and combined-filter API tests. | T-1 | Done |
| T-3 | Document the label API contract and run regression verification. | AC-1–AC-5 | README review; `.venv/bin/python -m pytest tests/test_api.py -k 'label or defaults_to_incomplete' -q` (14 passed); `.venv/bin/python -m pytest -q` (65 passed). | T-1, T-2 | Done |

## Traceability

| Acceptance criterion | Task(s) | Test/check | Coverage |
|---|---|---|---|
| AC-1 | T-1 | Maximum count, trimmed-length boundaries, invalid list/value tests | Covered |
| AC-2 | T-1 | Trim, lowercase, duplicate removal, first-seen order test | Covered |
| AC-3 | T-1 | Creation and list response assertions | Covered |
| AC-4 | T-2 | Trimmed/lowercase query, exact matching, single result, empty-result, and filter-composition tests | Covered |
| AC-5 | T-1–T-3 | Existing request defaults, existing filter tests, `.venv/bin/python -m pytest -q` | Covered |

## Deferred work

- None in the requested API slice. UI, persistence, authentication, and label mutation remain out of scope.
