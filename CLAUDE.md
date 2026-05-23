# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This repo authors and packages **Agent Skills** that teach AI agents how to safely drive a running `dikw-core` client (`dikw client *` commands) for knowledge-base observation, retrieval, import, curation, and task workflows. It contains almost no runtime logic of its own — the bulk is Markdown skill content plus a small Python toolchain (`src/dikw_skills/`) that validates, syncs, and packages that content for multiple agent platforms (Codex, Claude Code, OpenClaw, Hermes).

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

Without `uv`, set `PYTHONPATH=src` and invoke the modules with Python 3.12+ (e.g. `python -m dikw_skills.cli` is not wired; use the `*_main` entry points in `cli.py`).

## Architecture

The Python package in `src/dikw_skills/` is built around one central contract:

- **`catalog.py`** — `EXPECTED_SKILLS` maps each skill name to the exact `dikw client` subcommands it owns. This is the single source of truth that every other module consults. Every command appears under exactly one skill (ownership is non-overlapping, enforced by `validate`).
- **`validate.py`** — checks each `skills/<name>/SKILL.md` exists, has `name`/`description` frontmatter, and literally contains the string `dikw client <command>` for every command in its catalog entry; checks for duplicate command ownership; validates the Codex `plugin.json` and `.agents/plugins/marketplace.json` shapes; then folds in `check_sync`.
- **`sync.py`** — `sync_plugin` mirrors `skills/` into `plugins/dikw-skills/`; `check_sync` does a byte-level comparison (`filecmp.cmp(shallow=False)`) and reports stale or missing copies. The plugin copies are generated artifacts — **never hand-edit `plugins/dikw-skills/skills/`**; edit the canonical sources and re-sync.
- **`build.py`** — runs `sync_plugin` first, then produces per-skill zips, the plugin zip, two identical discovery indexes (`.well-known/skills/` and `.well-known/agent-skills/`), and a `checksums.txt`. `_safe_output_dir` refuses to build into the repo root, a parent, or any source directory — preserve this guard when changing build paths.

Data flow: **edit `skills/` → `sync_plugin` mirrors to plugin wrapper → `build_dist` packages everything into `dist/`.** `validate` and `--check` exist to catch drift between these stages in CI.

### Skill content conventions

Each skill lives in `skills/<name>/` with:
- `SKILL.md` — YAML frontmatter (`name` must equal the directory name; `description` required) followed by the agent-facing SOP. Body must mention each owned `dikw client <command>` verbatim or validation fails.
- `agents/openai.yaml` — Codex/OpenAI interface metadata (display name, default prompt).

When **adding or renaming a skill or command**: update `EXPECTED_SKILLS` in `catalog.py`, the `SKILL.md`, then run `sync-plugin` and the full baseline. The expected-artifact set in `tests/test_sync_and_build.py` is hard-coded per skill — update it too.

### Scope boundaries baked into the skills

- Only `dikw client *` commands are in scope. Root commands (`dikw init`, `dikw serve`, `dikw auth`) are setup *prerequisites*, documented in `README.md`, never owned by a skill.
- Skills assume data-returning `dikw client` commands default to JSON, so `--format json` is usually not added (pass `--format table` only for human output). Blocking/progress wrappers such as `tasks wait` and `serve-and-run` are exceptions: use `--plain` when piping and avoid `serve-and-run` for strict JSON parsing. Probe `dikw client health` before assuming reachability, and **do not** do final LLM answer synthesis with dikw-core (the agent composes answers from retrieved chunks/pages). Keep new skill content consistent with these defaults.

## Working conventions

These guidelines reduce common LLM coding mistakes; they bias toward caution over speed, so use judgment on trivial tasks.

### Think before coding
**Don't assume, don't hide confusion, surface tradeoffs.** State assumptions explicitly and ask when uncertain. If a request has multiple plausible interpretations, present them rather than picking silently. If a simpler approach exists, say so — push back when warranted. If something is unclear, stop, name what's confusing, and ask before implementing.

### Simplicity first
**Write the minimum code that solves the problem; nothing speculative.** No features beyond what was asked, no abstractions for single-use code, no "flexibility" or "configurability" that wasn't requested, no error handling for impossible scenarios. If 200 lines could be 50, rewrite it. The architecture above is deliberately organised around one central contract (`catalog.py`) for this reason — keep new code in the same spirit, and ask whether a senior engineer would call it overcomplicated.

### Surgical changes
**Touch only what you must; clean up only your own mess.** When editing existing code, don't "improve" adjacent code, comments, or formatting; don't refactor what isn't broken; match existing style even if you'd do it differently. If you notice unrelated dead code, mention it — don't delete it. Remove only the imports/variables/functions that *your* changes orphaned. Every changed line should trace directly to the user's request. (Concretely here: `plugins/dikw-skills/skills/` is generated by `sync.py` — edit the canonical `skills/` and re-sync; never hand-edit the plugin copies.)

### Goal-driven execution
**Define success criteria up front, then loop until verified.** Transform tasks into verifiable goals: "add validation" → write tests for invalid inputs, then make them pass; "fix the bug" → write a test that reproduces it, then make it pass; "refactor X" → tests pass before and after. For multi-step work, state a brief plan with a verify step per item. In this repo the verify step is the four-command baseline at the top of `## Commands` — running it green is the goal-driven exit condition. Strong criteria let the loop run independently; weak criteria ("make it work") force constant clarification.

These conventions are working if diffs contain fewer unnecessary changes, fewer rewrites due to overcomplication, and clarifying questions arrive before implementation rather than after mistakes.
