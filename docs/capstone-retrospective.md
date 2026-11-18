# Capstone feature review and team practices

## Evidence reviewed

The four `capstone/*` branches and their feature commits are in the merged `main` history:

| Branch | Implemented feature |
|---|---|
| `capstone/deadlines` | Optional due dates, computed due status, and due-date/status filters |
| `capstone/labels` | Validated and normalized labels, plus label filtering |
| `capstone/dependencies` | Task prerequisite links with validation |
| `capstone/task-completion-guard` | Completion blocked while direct prerequisites remain incomplete |

The implementations preserve the in-memory API and add focused tests and README contract updates. The current `develop` checkout's complete test command, `.venv/bin/python -m pytest -q`, passed with **79 passed** and one existing Starlette/httpx deprecation warning. The priority handoff's previous checkout and test snapshot was stale; see [task-priority handoff](./handoffs/task-priority.md).

## Observations

- The feature slices build on one another: labels and deadlines extend the list filters, then prerequisite links enable guarded completion.
- Approved requirements and traceable acceptance criteria helped bound the deadlines and labels work. The dependency stories instead rely on live Jira criteria, with some earlier focused-test commands not retained in the delivery log.
- Focused API tests, regression runs, and README contract updates recur across the branches; the repository's full suite currently exercises all integrated behavior.
- Handoffs can become stale as branches advance: the priority handoff described modified source files and only three API routes, while the current checkout has no tracked source edits and includes the completion endpoint.
- Several useful next behaviors were explicitly excluded from the delivered slices. They are candidates for review, not approved scope.

## Possible next features

1. **Edit task details after creation.** Allow selected fields such as title, priority, due date, labels, or dependencies to be corrected. Define which fields are mutable and preserve the existing validation rules. Priority and due-date changes were previously out of scope.
2. **Task lifecycle and dependency maintenance.** Decide whether tasks may be started or reopened, and whether dependencies may be edited. Specify what reopening or changing a prerequisite means for already-completed downstream tasks before implementing it.
3. **Durable, multi-user task storage.** Replace the in-memory-only lifecycle only if the product needs tasks to survive restarts or be isolated by user. Persistence and authentication remain explicit non-goals for this teaching application.
4. **Paged list retrieval with deterministic ordering.** Consider pagination if task volume grows; first resolve equal-priority ordering so clients can page through a stable result set.

## Team practices

| Practice | Trigger | Expected behavior | Accountable owner | One-month review signal |
|---|---|---|---|---|
| **Approve behavior before implementation** | A story changes API behavior, combines filters, or has unresolved edge cases. | Record the source, acceptance criteria, scope exclusions, dependencies, and open decisions; obtain human approval for the behavior before implementation begins. | Product/request owner | In a sample of completed stories, count those that started with approved criteria and those reopened because a behavior decision was missing. |
| **Verify each API slice and its contract** | A change adds or alters a request, response, validation rule, or endpoint. | Add focused behavior tests, retain compatibility/regression coverage, update the API documentation, then record focused and full-suite results. | Implementing engineer | Percentage of sampled API changes with passing focused/full test evidence and matching API documentation. |
| **Make dependencies explicit before sequencing work** | A story relies on another story or branch. | Record the prerequisite and its acceptance evidence; start dependent implementation from the agreed base after the prerequisite is integrated and verified. | Technical lead or story coordinator | Number of dependency-related integration rework events in the month. |
| **Keep handoffs synchronized with repository state** | A task is marked done or work moves to another session/owner. | Record the actual branch/commit, changed files, decisions and blockers, plus exact verification commands and results; refresh or remove obsolete state claims. | Current task owner | Number of sampled handoffs with stale branch, file-state, or test-result claims. |
| **Require human approval for external writes and releases** | Any action would write to an external system or publish, merge, deploy, or release a change. | Prepare the proposed action and evidence; obtain explicit approval from the accountable human before the write or release, then verify the resulting state. Tools or automation must not self-approve. | Maintainer or release owner | Percentage of sampled external writes/releases with prior human approval and recorded post-action verification; target 100%. |
