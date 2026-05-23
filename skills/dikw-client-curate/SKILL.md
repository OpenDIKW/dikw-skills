---
name: dikw-client-curate
description: Curate and govern a dikw-core base with mutating or cost-bearing `dikw client` workflows. Use for indexing, synthesis, wisdom distillation/review, lint scans/fixes, and eval gates with `dikw client ingest`, `dikw client synth`, `dikw client distill`, `dikw client eval`, `dikw client lint`, `dikw client lint propose`, `dikw client lint proposals`, `dikw client lint apply`, `dikw client review list`, `dikw client review approve`, or `dikw client review reject`.
---

# DIKW Client Curate

Use this skill for operations that refresh indexes, write generated knowledge,
call configured LLM/provider legs, or approve/reject wisdom candidates. Confirm
intent before applying fixes or approving/rejecting review items.

## Agent Default

Long-running mutating commands default to async and print a JSON task handle.
Use that path first so the agent can poll, resume, cancel, or hand off:

```bash
dikw client ingest
dikw client synth
dikw client distill
dikw client eval
dikw client lint propose --limit 10
dikw client lint apply <proposal_task_id> --pick 0,2
```

Capture `task_id` from stdout, then use `dikw-client-utils` (`tasks events`,
`tasks status`, `tasks wait`, or `tasks cancel`) to follow the task. Use
blocking shortcuts only when the user explicitly wants this invocation to wait
for the final report.

## Index Refresh

Run ingest after users add or import sources:

```bash
dikw client ingest
dikw client ingest --no-embed
```

- Use `--no-embed` for FTS-only refreshes without embedding API calls.
- Use `dikw client ingest --strict --plain` only when any per-file error should
  fail the run immediately; `--strict` implies waiting for completion.
- For task follow-up, use `dikw-client-utils`.

## Knowledge and Wisdom Production

Generate K-layer wiki pages:

```bash
dikw client synth
dikw client synth --all
dikw client synth --no-embed
```

Distill W-layer candidates:

```bash
dikw client distill
dikw client distill --batch 8
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
dikw client lint propose --limit 10
dikw client lint propose --rule broken_wikilink
dikw client lint propose --rule missing_provenance
dikw client lint proposals
```

`missing_provenance` (added in dikw-core 0.2.6) is a deterministic fixer — like
`broken_wikilink`, it reconciles a K-page frontmatter `sources:` against the
actual provenance edges in storage without an LLM call, so `--enable-llm` is
not needed.

Apply selected fixes only after inspecting proposals:

```bash
dikw client lint apply <proposal_task_id> --pick 0,2
dikw client lint apply <proposal_task_id> --skip 1
```

Use `--enable-llm` only when the user accepts token cost for fixer fallback
paths.

## Eval Gates

Run evals on the server:

```bash
dikw client eval
dikw client eval --dataset mvp --retrieval hybrid
dikw client eval --eval retrieval
dikw client eval --eval synth --judge --judge-sample 5
```

Default non-wait eval output is a task handle. For blocking eval reports,
`--pretty` changes report rendering; exit `1` means task/gate failure and exit
`2` means explicit synth eval had no declared synth threshold gate.

## Blocking Shortcuts

Use `--wait --plain` for short tasks or when the user explicitly asks for the
final report in the current command:

```bash
dikw client ingest --wait --plain
dikw client synth --wait --plain
dikw client lint propose --limit 10 --wait --plain
dikw client lint apply <proposal_task_id> --pick 0,2 --wait --plain
dikw client eval --dataset mvp --eval retrieval --wait --plain
```

## Safety Rules

- Prefer async submit plus `dikw-client-utils` for long-running tasks.
- Do not apply lint proposals, approve wisdom, or reject wisdom without an
  explicit user decision.
- Mention possible provider/LLM/embedding cost before `synth`, `distill`,
  `eval --judge`, or `lint propose --enable-llm`.
- Use `--wait --plain` only for bounded tasks or explicit synchronous requests.
