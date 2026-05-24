# DIKW Skills

[![CI](https://github.com/OpenDIKW/dikw-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/OpenDIKW/dikw-skills/actions/workflows/ci.yml)

Agent Skills and local plugin packaging for `dikw client *` workflows.

This repository treats `skills/` as the canonical source and packages those
skills for Codex, Claude Code, OpenClaw, and Hermes-compatible discovery flows.
The skills help agents use a running `dikw-core` client safely for observation,
retrieval, import, curation, and task utilities.

## Features

- Document the `dikw client` command surface as focused agent skills.
- Keep `dikw init`, `dikw serve`, and `dikw auth` as prerequisites, not skill triggers.
- Package canonical skills into the `plugins/dikw-skills/` local plugin wrapper.
- Generate individual skill archives, a plugin archive, registry indexes, and checksums.
- Validate command ownership, skill frontmatter, plugin sync, and release artifacts.

## Repository Layout

| Path | Purpose |
|---|---|
| `skills/` | Source-of-truth skill folders with `SKILL.md` (self-contained — no external references). |
| `plugins/dikw-skills/` | Local plugin wrapper for Codex, Claude Code, and OpenClaw. |
| `.agents/plugins/marketplace.json` | Codex local marketplace entry. |
| `.claude-plugin/marketplace.json` | Claude Code marketplace entry (plugin manifest lives at `plugins/dikw-skills/.claude-plugin/plugin.json`). |
| `src/dikw_skills/` | Validation, plugin sync, registry, and release build tooling. |
| `registry/` | OpenClaw and Hermes publication metadata. |
| `dist/` | Generated release artifacts, ignored by Git. |

Generated plugin skill copies under `plugins/dikw-skills/skills/` are synced
from the canonical `skills/` directory and should not be maintained by hand.

## Skill Catalog

| Skill | Purpose |
|---|---|
| `dikw-client-observe` | Inspect server/base/provider state with read-only client checks. |
| `dikw-client-retrieve` | Retrieve chunks, read pages, walk graph links, and fetch assets. |
| `dikw-client-import` | Pre-flight and import local source material, including converter-backed formats. |
| `dikw-client-curate` | Refresh indexes, synthesize K-layer pages, distill/review W-layer items, lint, and eval. |
| `dikw-client-utils` | Handle async task lifecycle and `serve-and-run` one-shot workflows. |

## Install in Claude Code

These skills ship as a Claude Code plugin. Add the marketplace, then install:

```text
/plugin marketplace add OpenDIKW/dikw-skills
/plugin install dikw-skills@opendikw
```

The five skills then appear namespaced as `dikw-skills:dikw-client-*`. (For
Codex, use the `.agents/plugins/marketplace.json` entry; OpenClaw/Hermes consume
the indexes under `registry/`.)

## Prerequisites

Install `dikw-core` from PyPI to provide the `dikw` CLI. Any installer works
(use the `cjk` extra by default so Chinese/CJK bases have the tokenizer):

```bash
pip install "dikw-core[cjk]"          # into the active venv (simplest)
pipx install "dikw-core[cjk]"         # isolated, on PATH
uv tool install "dikw-core[cjk]"      # isolated, on PATH (uv users)
```

Converters are plugins `dikw client` discovers in-process, so install them into
the **same environment as `dikw-core`**, only when importing non-Markdown inputs:

```bash
# Same venv as dikw-core:
pip install dikw-converter-mineru    # engine "mineru": .pdf/.docx/.pptx/.xlsx
pip install dikw-converter-epub      # engine "epub": .epub

# If dikw-core is an isolated tool, inject into that env instead:
uv tool install "dikw-core[cjk]" --with dikw-converter-mineru   # uv
pipx inject dikw-core dikw-converter-mineru              # pipx
```

All listed PyPI packages require Python `>=3.12`.

## Development

Run the quality baseline:

```bash
uv run dikw-skills-validate
uv run dikw-skills-sync-plugin --check
uv run python -m unittest discover -s tests
uv run dikw-skills-build
```

Without `uv`, set `PYTHONPATH=src` and run the modules directly with Python
3.12+.

## Distribution

Build release artifacts locally:

```bash
uv run dikw-skills-build
```

Artifacts are written under `dist/`:

| Path | Contents |
|---|---|
| `dist/skills/*.zip` | Individual skill archives. |
| `dist/plugins/dikw-skills-plugin.zip` | Plugin wrapper archive. |
| `dist/site/.well-known/skills/index.json` | Skills discovery index. |
| `dist/site/.well-known/agent-skills/index.json` | Agent Skills discovery index. |
| `dist/checksums.txt` | SHA-256 checksums. |
