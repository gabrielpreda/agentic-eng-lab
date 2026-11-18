# Task labels — feature specification

**Status:** Implemented  
**Requirements:** `docs/requirements/capstone-labels.md`  
**Source design:** [Miro tasks/labels](https://miro.com/app/board/uXjVENzs_98=/), diagram widget `3458764690519926990`

## Outcome and scope

Task API clients can assign up to five normalized labels when creating a task and list tasks with a chosen label. The change is additive: existing task request fields, endpoints, and filters remain available.

## Behavior and constraints

| Spec ID | Observable behavior or constraint | Source AC |
|---|---|---|
| S-1 | Omitted labels default to an empty list. Supplied labels are a list of up to five strings; each trimmed value is 1–24 characters. Invalid values return 422. | AC-1 |
| S-2 | Normalize labels by trimming and lowercasing; remove duplicates while preserving first-seen order. | AC-2 |
| S-3 | Creation and list responses include each task's normalized labels. | AC-3 |
| S-4 | `GET /tasks?label=value` trims and lowercases the query, matches exact normalized labels, returns each task once, and returns `200 []` for no matches. Existing filters compose with it. | AC-4 |
| S-5 | Preserve existing request fields, routes, in-memory behavior, and requests that omit labels. | AC-5 |

## Exclusions

- UI, persistence, authentication, predefined label catalog, or label updates after task creation.
- Multiple-label selection in one query; the Miro flow selects one label per request.

## Verification

| Spec ID | Verification | Result |
|---|---|---|
| S-1–S-5 | Focused label and compatibility API tests: `.venv/bin/python -m pytest tests/test_api.py -k 'label or defaults_to_incomplete' -q` | Passed: 14 tests |
| S-1–S-5 | `.venv/bin/python -m pytest -q` | Passed: 65 tests |

## Implementation notes

- Label count is validated on the supplied list before duplicate removal, as the Miro flow checks the five-item limit before normalization/deduplication.
- Label query validation is intentionally limited to the Miro-defined trim/lowercase/match behavior; a non-matching query yields an empty result.
