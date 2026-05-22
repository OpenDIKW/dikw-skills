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
