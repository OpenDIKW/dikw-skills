---
name: dikw-client-utils
description: Manage DIKW client utility workflows for async tasks and one-shot local server lifecycles. Use only for `dikw client tasks list`, `dikw client tasks status`, `dikw client tasks events`, `dikw client tasks wait`, `dikw client tasks cancel`, and `dikw client serve-and-run`.
---

# DIKW Client Utils

Use this skill for the async task lifecycle and for temporary server wrappers. Do not add unrelated DIKW commands here.

## Task listing and snapshots

`dikw client tasks list` returns one cursor page as the server envelope `{tasks, next_cursor, has_more}`.
Each row is a **summary**: it omits `result` and `error`. Read a task's full body or terminal payload with `dikw client tasks status <task_id>`, never from the list.

```bash
dikw client tasks list
dikw client tasks list --op ingest --status running --limit 20
dikw client tasks list --all                  # drain the cursor into a flat array
dikw client tasks list --cursor <next_cursor> # resume from a prior page
dikw client tasks status <task_id>
```

- `--limit` is the page size (default 100, max 1000), not a total cap. Pair it with `--cursor` to walk a large queue, or pass `--all` to collect every page.
- The filters (`--op`, `--status`) work together with the cursor.
- Task ids are opaque strings. Do not assume a length or an encoding. Always pass the exact `task_id` that the server returned.
- Async submit commands print `task_id`, `status`, `events_url`, and `wait_command`.

## Cursor event SOP

Fetch one cursor page:

```bash
dikw client tasks events <task_id> --from-seq 0 --limit 100 --wait 30
```

- The response has `events`, `next_from_seq`, `has_more`, `last_seq`, and `task_status`.
- Advance with `next_from_seq`.
- Stop only after `task_status` is terminal and you have seen the final event or result.
- `--wait` is the server hold time in seconds (0–60). `0` returns a snapshot.

Use cursor events when you need custom polling or partial progress. Use `wait` for an ordinary blocking flow.

## Wait and cancel SOP

Block until the task is terminal:

```bash
dikw client tasks wait <task_id> --plain
dikw client tasks wait <task_id> --poll-wait 30 --timeout 600 --plain
```

Cancel only when the user asks for it, or when a local timeout should also stop the server work:

```bash
dikw client tasks cancel <task_id>
dikw client tasks cancel <task_id> --pretty
```

Exit code mapping:

- succeeded=0
- failed=1
- cancelled=130
- timeout=124

A timeout does not cancel the server work. Chain `tasks cancel` if the work must stop.

Done when the task is terminal and you have reported its final status and result (or error).

## Serve and run

Use `serve-and-run` for a one-shot local server around one inner client command:

```bash
dikw client serve-and-run --base ./my-base -- status
dikw client serve-and-run --base ./my-base -- ingest --no-embed
dikw client serve-and-run --keep-alive --base ./my-base -- retrieve "question"
```

- Without `--keep-alive`, async inner commands are forced to wait, so the temporary server is not stopped before the task completes.
- With `--keep-alive`, the server keeps running after the inner command and prints its connection details.
- `--host 0.0.0.0` (any non-loopback host) requires `--token`.

Avoid `serve-and-run` when a machine must parse clean JSON from stdout. The temporary server and its libraries can write startup and status logs into the same stream.
For strict JSON parsing, attach to a running `dikw serve` and call the `dikw client ...` command directly.

This skill documents the full async task contract above. The `task_id` / `next_from_seq` cursor shape and the exit codes need no external file.
