# CLAUDE.md

Guidance for Claude Code in the `dikw-skills` repository.

## What this repo is

This repo writes and packages **Agent Skills** that teach AI agents to drive a running `dikw-core` safely through `dikw client *` commands: observation, retrieval, import, curation, and task workflows.
It has almost no runtime logic. Most of it is Markdown skill content, plus a small Python toolchain (`src/dikw_skills/`) that validates, syncs, and packages that content for Codex, Claude Code, OpenClaw, and Hermes.

`skills/` is the **canonical source of truth**. Everything else (the plugin wrapper, registry indexes, dist archives) is derived from it.

## Commands

```bash
# Full quality baseline (run all four before committing)
uv run dikw-skills-validate          # validate frontmatter, command ownership, manifests, sync
uv run dikw-skills-sync-plugin --check   # fail if plugin copies are stale
uv run python -m unittest discover -s tests
uv run dikw-skills-build             # write release artifacts to dist/

# Regenerate the plugin wrapper after editing skills/
uv run dikw-skills-sync-plugin       # copies skills/ into plugins/dikw-skills/

# Run a single test
uv run python -m unittest tests.test_sync_and_build.SyncAndBuildTests.test_build_creates_expected_release_artifacts
```

Without `uv`, set `PYTHONPATH=src` and call the modules with Python 3.12+. `python -m dikw_skills.cli` is not wired; use the `*_main` entry points in `cli.py`.

## Architecture

The package in `src/dikw_skills/` is built around one central contract:

- **`catalog.py`** — `EXPECTED_SKILLS` maps each skill name to the exact `dikw client` subcommands that it owns. Every other module reads it. Each command has exactly one owner; `validate` enforces this.
- **`validate.py`** — checks that each `skills/<name>/SKILL.md` exists, has `name` / `description` frontmatter, and contains the literal string `dikw client <command>` for every command it owns. It also checks for duplicate ownership, validates the Codex `plugin.json` and `.agents/plugins/marketplace.json` shapes, and runs `check_sync`.
- **`sync.py`** — `sync_plugin` mirrors `skills/` into `plugins/dikw-skills/`. `check_sync` compares bytes (`filecmp.cmp(shallow=False)`) and reports stale or missing copies.
- **`build.py`** — runs `sync_plugin` first, then writes per-skill zips, the plugin zip, two identical discovery indexes (`.well-known/skills/` and `.well-known/agent-skills/`), and `checksums.txt`. `_safe_output_dir` refuses to build into the repo root, a parent, or any source directory. Keep this guard when you change build paths.

Data flow: **edit `skills/` → `sync_plugin` mirrors to the plugin wrapper → `build_dist` packages everything into `dist/`.** `validate` and `--check` catch drift between these stages in CI.

**WARNING:** `plugins/dikw-skills/skills/` is generated. Never edit it by hand. Edit `skills/` and run `uv run dikw-skills-sync-plugin`.

### Skill content conventions

Each skill lives in `skills/<name>/` with:

- `SKILL.md` — YAML frontmatter (`name` equals the directory name; `description` is required), then the agent-facing SOP. The body must contain each owned `dikw client <command>` verbatim, or validation fails.
- `agents/openai.yaml` — Codex/OpenAI interface metadata (display name, short description, default prompt).

When you **add or rename a skill or a command**:

1. Update `EXPECTED_SKILLS` in `catalog.py`.
2. Update the `SKILL.md`.
3. Update the hard-coded sets in `tests/test_catalog.py` and the expected artifacts in `tests/test_sync_and_build.py`.
4. Run `sync-plugin` and the full baseline.

### Version

The package version appears in `pyproject.toml`, `uv.lock`, `build.PACKAGE_VERSION`, `.claude-plugin/marketplace.json`, both plugin manifests, and `registry/*.json`. Change all of them together. `tests/test_catalog.py` checks that they agree.

### Scope boundaries baked into the skills

- Only `dikw client *` commands are in scope. Root commands (`dikw init`, `dikw serve`, `dikw auth`) are setup prerequisites, documented in `README.md`. No skill owns them.
- Data-returning `dikw client` commands default to JSON, so the skills do not add `--format json`. They use `--format table` only for human output.
- Blocking and progress wrappers (`tasks wait`, `--wait`) are exceptions: use `--plain` when stdout is piped. Avoid `serve-and-run` when stdout must be strict JSON.
- Probe `dikw client health` before you assume the server is reachable.
- `dikw-core` never writes the final answer. The agent composes answers from retrieved chunks and pages.

## Writing product skills

These skills run in other people's agents, on several platforms. Write them for that reader.

- **Frontmatter:** use only Agent Skills spec fields (`name`, `description`, and optionally `license`, `compatibility`, `metadata`, `allowed-tools`). Claude Code-only fields (`disable-model-invocation`, `context`, `paths`, …) break packaging for other platforms.
- **Description:** put the main use case first, then the owned commands. A description must parse as YAML: do not put `: ` inside an unquoted value.
- **Each SOP says when it is done.** End a workflow with a "Done when …" line: a state that the agent can check.
- **Each mutating or token-costing command says when to stop and ask.** The agent must get an explicit user decision before it changes or deletes content, or spends tokens.
- **Grounding:** a retrieval answer cites the page path of each claim, and marks each claim that the evidence does not support.
- **Commands must match the current `dikw-core` CLI.** Check each command and flag against `dikw client <command> --help` from the `dikw-core` version you target.
- **Write plainly:** short sentences, one instruction per sentence, the same word for the same thing.

## Working rules

### Clarify before coding

- State your assumptions.
- If a request has more than one reading, show them. Do not pick one silently.
- If a decision blocks you, ask one question with the AskUserQuestion tool. Put your recommended answer first.
- If a simpler approach exists, say so before you write code.

### Keep the change small

- Write the minimum code that solves the request. No speculative features, no single-use abstractions, no flexibility that nobody asked for, no error handling for impossible cases.
- Keep new code organised around the one central contract (`catalog.py`).
- Change only what the request needs. Match the existing style.
- Report unrelated dead code. Do not delete it. Remove only what your change made unused.

### Test first

- Turn the request into a check: "add validation" → tests for invalid input; "fix the bug" → a failing test that reproduces it; "refactor X" → tests pass before and after.
- The check for every change is the four-command baseline in `## Commands`. Green on all four is the finish condition.

## Autonomy

- When a step does not need my input, continue. Put status notes in the same message as your next action.
- Stop and ask only when you cannot continue without my decision, or before a destructive action: delete data or files you did not create, force-push, or change anything outside this repository.
- Do not end a turn with a summary that announces the next step but does not take it, or with an offer to continue "unless you prefer otherwise".

## Finish line

A change is done when the four-command baseline is green, the PR is merged, and local `main` is synced.

## Report

End every run with three headings: **需要你决定** (decisions you wait for; "无" if none), **改动** (what changed, with PR links), **发现** (what you found; mark each claim you could not confirm, and say where you looked).
