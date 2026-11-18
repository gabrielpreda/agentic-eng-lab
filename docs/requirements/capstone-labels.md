# Task labels — requirements

**Status:** Implemented from the user request and Miro source  
**Source request:** User request in this session  
**Approval owner:** Gabriel Preda

## User outcome

Teams can organize tasks by project or workstream and retrieve tasks carrying a chosen label, while existing task requests and API behavior continue to work.

## Sources reviewed

| Source | Evidence | Limits or status |
|---|---|---|
| User request | Teams need to organize tasks by project or workstream; add labels and allow viewing tasks by a chosen label; preserve existing tasks and clients. | Does not define label validation or filter normalization. |
| [Miro board: tasks/labels](https://miro.com/app/board/uXjVENzs_98=/), diagram widget `3458764690519926990` | Create flow: optional labels; omitted labels become an empty list; trim; at most five; each trimmed label has 1–24 characters; lowercase and deduplicate, preserving first-seen order. Filter flow: choose one label, trim and lowercase query, return matching tasks once, or `200` with an empty list. | One diagram item read; no controlled label catalog or update flow shown. |
| [Current API](../../app/main.py) and [API tests](../../tests/test_api.py) | Tasks are created and listed in memory; list filters include completion, priority, due status, and due date. | No label behavior existed before this change. |
| [README API contract](../../README.md) | Documents the existing request and response shape. | Updated to document labels and the label filter. |
| Jira BWAA project | Current issue list and a label-related JQL search showed no existing task-label story; project supports Story and Task issue types. | Used to check existing work and target the requested story batch, not as a product-requirement source. |

## Confirmed facts

- Labels may be omitted on task creation; omitted labels are stored and returned as an empty list.
- A supplied label list may contain at most five entries.
- Each label must contain 1–24 characters after surrounding whitespace is trimmed.
- Labels are lowercased and duplicate normalized values are removed while retaining first-seen order.
- `GET /tasks?label=value` trims and lowercases the chosen label, returns each matching task once, and returns `200` with an empty array when none match.

## Assumptions and inferences

- Labels are free-form strings because the Miro diagram defines no predefined catalog.
- Existing list filters continue to compose: a task must match every supplied filter, including the new label filter.
- Invalid label types and malformed label lists use the API's existing FastAPI/Pydantic `422` validation behavior.
- `labels` is an additive response property so clients can see the assigned labels; omitted request fields and existing routes remain valid.

## Acceptance criteria

1. **AC-1:** `POST /tasks` accepts an optional list of labels. Omission produces `[]`. At most five entries are accepted; each entry must be a string with 1–24 characters after trimming. Invalid counts, values, or shapes return HTTP 422.
2. **AC-2:** Accepted labels are trimmed and lowercased. Duplicate normalized labels are removed, keeping the first occurrence and list order.
3. **AC-3:** Every task in successful `POST /tasks` and `GET /tasks` responses includes its normalized `labels` array.
4. **AC-4:** `GET /tasks?label=value` trims and lowercases the query value and returns tasks whose labels contain that exact normalized value. Each matching task appears once; no matches return HTTP 200 with `[]`. The filter composes with existing list filters.
5. **AC-5:** Existing request fields, endpoints, in-memory storage, and non-label behavior remain available. Requests without labels continue to work and produce tasks with `labels: []`.

## Constraints and non-goals

- Keep the existing in-memory store and task endpoints.
- No UI, persistence, authentication, fixed label catalog, or label-update endpoint is requested.
- The label query follows the Miro flow's trim/lowercase-and-match behavior; it does not introduce a separate label catalog or mutation workflow.
