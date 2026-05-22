---
name: dikw-client-observe
description: Inspect a running dikw-core server using read-only `dikw client` commands. Use when an agent needs to attach to a DIKW base, confirm server health, inspect storage counts, verify provider connectivity, or collect status with `dikw client info`, `dikw client status`, `dikw client health`, or `dikw client check`.
---

# DIKW Client Observe

Use this skill for read-only attachment and diagnostics against a running
`dikw serve` instance.

## Prerequisites

Confirm `dikw-core` is installed (`pip install dikw-core`, or `pipx`/`uv tool`
if you prefer an isolated tool) and the user has a running `dikw serve`. Root
commands such as `dikw init`, `dikw serve`, and `dikw auth` are setup context,
not this skill's owned command surface.

## Command SOP

Start every new attach flow with:

```bash
dikw client health
```

Use the response to identify `base_root`, `version`, `storage_engine`,
`layer_counts`, and configured providers.

Use these read-only commands:

```bash
dikw client info
dikw client status
dikw client health
dikw client check
dikw client check --llm-only
dikw client check --embed-only
```

These commands default to JSON, so `--format json` is redundant. For humans,
add `--format table` where supported.

## Interpretation

- Treat `dikw client health` as the bootstrap probe.
- Treat `dikw client status` as storage/count inspection.
- Treat `dikw client check` as a provider connectivity gate.
- `dikw client check` exits `0` only when requested provider legs pass; exits
  `1` for failed probes and `2` for flag misuse.
- Do not use observe commands to refresh indexes or mutate content. Use
  `dikw-client-curate` for `ingest`, `lint apply`, `synth`, `distill`, or
  review decisions.
