# DIKW Client Command Reference

All commands talk to a running `dikw serve` instance unless wrapped by
`dikw client serve-and-run`.

## Shared options

- `--server`: server URL. Default is `DIKW_SERVER_URL` or `http://127.0.0.1:8765`.
- `--token`: bearer token. Default is `DIKW_SERVER_TOKEN` or client config.
- `--format json|table`: JSON is usually agent-facing; table is human-facing.
- `--plain`: disable rich progress/status output when piping command output.
- `--wait`: block until an async task reaches a terminal status.

## Command ownership

| Skill | Commands |
|---|---|
| `dikw-client-observe` | `dikw client info`, `dikw client status`, `dikw client health`, `dikw client check` |
| `dikw-client-retrieve` | `dikw client retrieve`, `dikw client pages list`, `dikw client pages get`, `dikw client pages links`, `dikw client graph get`, `dikw client assets get` |
| `dikw-client-import` | `dikw client import` |
| `dikw-client-curate` | `dikw client ingest`, `dikw client synth`, `dikw client distill`, `dikw client eval`, `dikw client lint`, `dikw client lint propose`, `dikw client lint proposals`, `dikw client lint apply`, `dikw client review list`, `dikw client review approve`, `dikw client review reject` |
| `dikw-client-utils` | `dikw client tasks list`, `dikw client tasks status`, `dikw client tasks events`, `dikw client tasks wait`, `dikw client tasks cancel`, `dikw client serve-and-run` |

## Agent defaults

- Prefer JSON output for parseable results.
- Add `--plain` when a command streams or renders progress and stdout will be parsed.
- Use `dikw client health --format json` before assuming the server is reachable.
- Do not perform final LLM answer synthesis with dikw-core. The agent composes an answer from retrieved chunks and pages.
