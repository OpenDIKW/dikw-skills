---
name: dikw-client-curate
description: Curate a dikw-core base with mutating or cost-bearing `dikw client` commands. Use for indexing, K-layer synthesis and its self-check, lint scans and fixes, eval gates, soft-deleting a document, and writing hand-authored W-layer pages, with `dikw client ingest`, `dikw client synth`, `dikw client eval`, `dikw client lint`, `dikw client lint propose`, `dikw client lint proposals`, `dikw client lint apply`, `dikw client delete`, or `dikw client wisdom write`.
---

# DIKW Client Curate

These commands refresh indexes, write knowledge, call the configured LLM or embedding provider, or delete documents.

## Stop and ask the user first

Ask before you run one of these, unless the user already asked for exactly that action:

- `lint apply` — it changes K-layer pages.
- `delete` — it removes a document from the index and moves its file to `<base>/trash/`.
- `wisdom write` — it creates a W-layer page or **overwrites** an existing one.
- A command that costs tokens: `synth`, `synth --judge`, `eval --judge`, `lint propose --enable-llm`. Tell the user that it calls the configured provider.

## Async by default

Long-running commands submit a server task and print a JSON handle (`task_id`, `status`, `events_url`, `wait_command`).

- Capture `task_id`. Follow it with `dikw-client-utils` (`tasks status`, `tasks events`, `tasks wait`, `tasks cancel`).
- Add `--wait --plain` only for a short task, or when the user wants the final report from this command.
- Exceptions: `delete` and `wisdom write` wait by default. Add `--no-wait` to get a task handle instead.

## Index refresh

```bash
dikw client ingest
dikw client ingest --no-embed
dikw client ingest --strict --plain
```

- `ingest` indexes the D-layer sources. Then it adds vectors to any D/K/W chunk that has none.
- It does **not** scan `knowledge/` or `wisdom/`. `synth` and `lint apply` index K pages; `wisdom write` indexes W pages.
- `--no-embed` refreshes full-text search only, with no embedding API calls.
- `--strict` fails the run when any file errors. It implies `--wait`.

Run `ingest` after the user adds or imports sources.

## K-layer synthesis

```bash
dikw client synth
dikw client synth --all
dikw client synth --no-embed
dikw client synth --verify --plain
dikw client synth --judge --plain
```

- `synth` writes K-layer pages from sources that it has not synthesised yet. `--all` synthesises every source again.
- `--verify` runs a self-check over this run's pages (persist, lint, semantic duplicate) and exits non-zero when it fails. It implies `--wait`.
- `--judge` adds a report-only grounding leg: an entailment ratio from an LLM judge. It never changes pass or fail. It needs an embedder, costs tokens, and implies `--verify`.

Done when the task succeeded and, with `--verify`, the self-check passed.

## Lint governance

Scan without changes:

```bash
dikw client lint
dikw client lint --format table
```

Propose fixes (an async task):

```bash
dikw client lint propose --limit 10
dikw client lint propose --rule broken_wikilink
dikw client lint propose --rule untracked_file
dikw client lint proposals
```

- `--rule` takes one lint kind: `broken_wikilink`, `orphan_page`, `duplicate_title`, `non_atomic_page`, `missing_provenance`, `missing_file`, `stale_index`, `untracked_file`, `dangling_provenance`, `invalid_wisdom_status`, `uncategorized`, `title_slug_quality`.
- Kinds without a fixer (for example `duplicate_title`, `dangling_provenance`, `uncategorized`) are accepted, but every issue lands in `skipped`.
- `--limit` caps the issues consumed (default 10, max 200).
- `--enable-llm` lets fixers call the LLM: the grounded `broken_wikilink` repair, the `non_atomic_page` splitter, and the `orphan_page` merge. It is off by default because each issue can cost tokens.
- `stale_index` and `untracked_file` find K or W files that were edited or restored by hand. `lint apply` then re-indexes the bytes on disk without running synth again.

Apply fixes only after the user has reviewed the proposals:

```bash
dikw client lint apply <proposal_task_id> --pick 0,2
dikw client lint apply <proposal_task_id> --skip 1
```

## Eval gates

```bash
dikw client eval
dikw client eval --dataset mvp --retrieval hybrid
dikw client eval --dataset mvp --eval retrieval
dikw client eval --dataset mvp --eval synth --judge --judge-sample auto
dikw client eval --dataset mvp --eval retrieval --write-baseline baseline.json
dikw client eval --dataset mvp --eval retrieval --against baseline.json
```

- The server reads the dataset. `--dataset` names a packaged dataset or a path on the server. Omit it to run every packaged dataset.
- `--retrieval` takes `hybrid` (default), `bm25`, `vector`, or `all`.
- `--write-baseline` and `--against` turn a run into a regression gate. Each needs one `--dataset` and one `--eval` mode, and implies `--wait`.
- `--judge` adds an LLM judge score to synth evals and costs tokens. `--judge-sample auto` judges a calibrated sample instead of every item.
- Exit codes with `--wait`: `0` succeeded and the gate passed; `1` failed or the gate failed; `130` cancelled; `2` an `--eval synth` run with no declared gate.

## Delete a document

```bash
dikw client delete knowledge/concept/old-note.md --reason "superseded"
dikw client delete sources/notes/draft.md
```

- `delete` works on D, K, and W paths. It removes the index rows and moves the file to `<base>/trash/<layer>/...` with a `trashed:` audit block.
- Links from other pages to the deleted page break. The next `dikw client lint` reports them as `broken_wikilink`; the delete report counts them in `inbound_broken`. Delete never rewrites another page.
- A path that is not registered fails the task. Find registered paths with `dikw client pages list`.
- To recover, move the file back. A source re-indexes on the next `ingest`. A K or W page re-indexes through `lint propose --rule untracked_file` and then `lint apply`.

## Write a W-layer page

The W layer is hand-written. Write only content that the user wrote or approved. Do not invent wisdom.

1. Check whether the page exists. `wisdom write` overwrites the same (author, slug):

   ```bash
   dikw client pages get wisdom/elon-musk/first-principles.md
   ```

2. Write the page:

   ```bash
   dikw client wisdom write --author elon-musk --slug first-principles \
     --title "First Principles" --body-file body.md \
     --status draft --tag mental-model --source sources/notes/interview.md
   ```

- `--slug` and `--title` are required. Give exactly one of `--body` or `--body-file`.
- `--author` and `--slug` are ASCII kebab-case. Without `--author`, the file is `wisdom/<slug>.md`.
- `--status` takes `draft`, `published`, `favorite`, or `archived`.
- Repeat `--tag` and `--source` for more than one. `--source` adds a provenance path.
- `--no-embed` defers embedding to the next `ingest`.

## Safety rules

- Prefer an async submit plus `dikw-client-utils` for long tasks.
- Do not run `lint apply`, `delete`, or `wisdom write` without an explicit user decision.
- Say that a command costs tokens before you run `synth`, `synth --judge`, `eval --judge`, or `lint propose --enable-llm`.
- Use `--wait --plain` only for bounded tasks or an explicit request for the final report.
