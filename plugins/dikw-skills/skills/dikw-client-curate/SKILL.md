---
name: dikw-client-curate
description: Curate and govern a dikw-core base with mutating or cost-bearing `dikw client` workflows. Use for indexing, synthesis, wisdom distillation/review, lint scans/fixes, and eval gates with `dikw client ingest`, `dikw client synth`, `dikw client distill`, `dikw client eval`, `dikw client lint`, `dikw client lint propose`, `dikw client lint proposals`, `dikw client lint apply`, `dikw client review list`, `dikw client review approve`, or `dikw client review reject`.
---

# DIKW Client Curate

Use this skill for operations that refresh indexes, write generated knowledge,
call configured LLM/provider legs, or approve/reject wisdom candidates. Confirm
intent before applying fixes or approving/rejecting review items.

## Async vs Blocking

Long-running mutating commands default to async and print a JSON task handle.
Prefer the async path when an agent can poll or resume later:

```bash
dikw client ingest
dikw client synth
dikw client lint propose --limit 10
```

Then use `dikw-client-utils` (`tasks events`, `tasks status`, `tasks wait`, or
`tasks cancel`) to follow the task. Use `--wait --plain` only when the user
expects this command invocation to block until a final report is available.

## Index Refresh

Run ingest after users add or import sources:

```bash
dikw client ingest --wait --plain
dikw client ingest --no-embed --wait --plain
dikw client ingest --strict --plain
```

- Use `--no-embed` for FTS-only refreshes without embedding API calls.
- Use `--strict` when any per-file error should fail the run; it implies wait.
- For async task follow-up, use `dikw-client-utils`.

## Knowledge and Wisdom Production

Generate K-layer wiki pages:

```bash
dikw client synth --wait --plain
dikw client synth --all --wait --plain
dikw client synth --no-embed --wait --plain
```

Distill W-layer candidates:

```bash
dikw client distill --wait --plain
dikw client distill --batch 8 --wait --plain
```

Review wisdom candidates:

```bash
dikw client review list
dikw client review approve W-xxxxxx
dikw client review approve W-xxxxxx --pretty   # colored human-readable line
dikw client review reject W-xxxxxx
```

`review approve` / `review reject` print the raw `{item_id, new_status}` JSON on
stdout by default (pipe straight to `jq`); pass `--pretty` for the colored human
line. Approve or reject only when the user has made the review decision clear.

## Lint Governance

Scan without applying changes:

```bash
dikw client lint
```

Propose fixes:

```bash
dikw client lint propose --limit 10 --wait --plain
dikw client lint propose --rule broken_wikilink --wait --plain
dikw client lint proposals
```

Apply selected fixes only after inspecting proposals:

```bash
dikw client lint apply <proposal_task_id> --pick 0,2 --wait --plain
dikw client lint apply <proposal_task_id> --skip 1 --wait --plain
```

Use `--enable-llm` only when the user accepts token cost for fixer fallback
paths.

## Eval Gates

Run evals on the server:

```bash
dikw client eval --wait --plain
dikw client eval --dataset mvp --retrieval hybrid --wait --plain
dikw client eval --eval retrieval --wait --plain
dikw client eval --eval synth --judge --judge-sample 5 --wait --plain
```

By default eval emits NDJSON-style report lines unless `--pretty` is used.
Treat exit `1` as task/gate failure and exit `2` on explicit synth eval with no
declared synth threshold gate.

## Safety Rules

- Prefer `--wait --plain` when the user expects a final report.
- Do not apply lint proposals, approve wisdom, or reject wisdom without an
  explicit user decision.
- Mention possible provider/LLM/embedding cost before `synth`, `distill`,
  `eval --judge`, or `lint propose --enable-llm`.
- For async task handles, waiting, events, cancellation, and exit codes, use
  the `dikw-client-utils` skill.
