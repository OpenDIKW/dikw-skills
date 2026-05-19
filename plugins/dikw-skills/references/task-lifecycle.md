# DIKW Client Task Lifecycle

Use this reference from `dikw-client-utils`, and from other skills only when
they submit async tasks.

## Async submit shape

Async commands return a JSON handle by default:

```json
{
  "task_id": "abc123def456",
  "status": "pending",
  "events_url": "/v1/tasks/abc123def456/events",
  "wait_command": "dikw client tasks wait abc123def456"
}
```

## Cursor events

Use `dikw client tasks events <task_id> --from-seq N --limit M --wait K` for
one cursor page. The response includes `events`, `next_from_seq`, `has_more`,
`last_seq`, and `task_status`.

Advance with the returned `next_from_seq`. Stop only when `task_status` is
terminal and the final payload has been observed.

## Waiting and cancellation

Use:

```bash
dikw client tasks wait <task_id> --plain
dikw client tasks cancel <task_id>
```

Exit code mapping:

- succeeded=0
- failed=1
- cancelled=130
- timeout=124

Timeouts do not cancel server-side work. Chain `dikw client tasks cancel` only
when the user wants cancellation.
