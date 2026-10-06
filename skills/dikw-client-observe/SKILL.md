---
name: dikw-client-observe
description: Inspect a running dikw-core server with read-only `dikw client` commands. Use when an agent attaches to a DIKW base, confirms server health, inspects storage counts, or verifies provider connectivity with `dikw client health`, `dikw client info`, `dikw client status`, or `dikw client check`.
---

# DIKW Client Observe

Use this skill for read-only attach and diagnostics against a running `dikw serve` instance.

## Prerequisites

- `dikw-core` is installed (`pip install "dikw-core[cjk]"`, or `pipx` / `uv tool` for an isolated tool). Use the CJK extra by default for Chinese/CJK bases.
- The user runs `dikw serve`.
- Root commands such as `dikw init`, `dikw serve`, and `dikw auth` are setup context. This skill does not own them.

## Attach SOP

1. Probe first:

   ```bash
   dikw client health
   ```

   Read `base_root`, `version`, `storage_engine`, `layer_counts`, and the configured providers.
   The response shows whether each provider key is present. It never shows the key.
2. If `health` fails, stop. Report the server URL you used and the error. Do not guess the server state.
   The URL comes from `--server`, else `$DIKW_SERVER_URL`, else `http://127.0.0.1:8765`.
3. Use the other read-only commands as needed:

   ```bash
   dikw client info
   dikw client status
   dikw client check
   dikw client check --llm-only
   dikw client check --embed-only
   ```

Done when you can state which base the server serves, its layer counts, and whether each provider leg passes.

## Output

- `health`, `status`, and `check` print JSON by default, so `--format json` is redundant. Add `--format table` for a human.
- `info` prints JSON only.

## Interpretation

- `dikw client health` is the bootstrap probe.
- `dikw client status` shows storage counts.
- `dikw client check` is the provider connectivity gate. It exits `0` only when the requested provider legs pass, `1` when a probe fails, and `2` on flag misuse.
- `check` makes small live calls to the LLM and embedding providers, so it spends a few tokens.
- Observe commands never refresh indexes or change content. Use `dikw-client-curate` for `ingest`, `synth`, `lint apply`, `delete`, or `wisdom write`.
