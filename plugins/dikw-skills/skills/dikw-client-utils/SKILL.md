---
name: dikw-client-utils
description: Manage DIKW client utility workflows for async tasks and one-shot local server lifecycles. Use only for `dikw client tasks list`, `dikw client tasks status`, `dikw client tasks events`, `dikw client tasks wait`, `dikw client tasks cancel`, and `dikw client serve-and-run`.
---

# DIKW Client Utils

Use this skill for task lifecycle handling and temporary server wrappers. Do
not add unrelated DIKW commands here.

## Task Listing and Snapshots

Inspect server-side tasks:

```bash
dikw client tasks list --format json
dikw client tasks list --op ingest --status running --limit 20 --format json
dikw client tasks status <task_id>
```

Task ids are 12-character hex identifiers. Async submit commands print a
`task_id`, `status`, `events_url`, and `wait_command`.

## Cursor Event SOP

Fetch one cursor page:

```bash
dikw client tasks events <task_id> --from-seq 0 --limit 100 --wait 30
```

The response includes `events`, `next_from_seq`, `has_more`, `last_seq`, and
`task_status`. Advance using `next_from_seq`. Stop only after `task_status` is
terminal and the final event/result has been seen.

Use cursor events when an agent needs custom polling or partial progress. Use
wait for ordinary blocking UX.

## Wait and Cancel SOP

Block until terminal:

```bash
dikw client tasks wait <task_id> --plain
dikw client tasks wait <task_id> --poll-wait 30 --timeout 600 --plain
```

Cancel only when the user requests cancellation or a local timeout should be
followed by server-side stop:

```bash
dikw client tasks cancel <task_id>
dikw client tasks cancel <task_id> --pretty
```

Exit code mapping:

- succeeded=0
- failed=1
- cancelled=130
- timeout=124

Timeouts do not auto-cancel server work.

## Serve and Run

Use `serve-and-run` for a one-shot local server around an inner client command:

```bash
dikw client serve-and-run --base ./my-base -- status
dikw client serve-and-run --base ./my-base -- ingest --no-embed
dikw client serve-and-run --keep-alive --base ./my-base -- retrieve "question"
```

Without `--keep-alive`, inner async operations are auto-forced to wait so the
temporary server is not torn down before the task completes.

Read `../../references/task-lifecycle.md` for the shared task contract.
