---
name: dikw-client-utils
description: Manage DIKW client utility workflows for async tasks and one-shot local server lifecycles. Use only for `dikw client tasks list`, `dikw client tasks status`, `dikw client tasks events`, `dikw client tasks wait`, `dikw client tasks cancel`, and `dikw client serve-and-run`.
---

# DIKW Client Utils

Use this skill for task lifecycle handling and temporary server wrappers. Do
not add unrelated DIKW commands here.

## Task Listing and Snapshots

`dikw client tasks list` returns a single cursor page as the server envelope
`{tasks, next_cursor, has_more}`. Each row is a **summary** — it omits `result`
and `error`, so read a task's full body or terminal payload through
`dikw client tasks status <task_id>`, never from the list view.

```bash
dikw client tasks list
dikw client tasks list --op ingest --status running --limit 20
dikw client tasks list --all                  # drain the cursor into a flat array
dikw client tasks list --cursor <next_cursor> # resume from a prior page
dikw client tasks status <task_id>
```

`--limit` is the page size (default 100, max 1000), not a total cap; pair it
with `--cursor` to walk a large queue page by page, or pass `--all` to collect
every page at once. Filters (`--op`, `--status`) compose with the cursor.

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

This skill documents the full async task contract inline above; the
`task_id` / `next_from_seq` cursor shape and exit codes need no external file.
