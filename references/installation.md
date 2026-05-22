# DIKW Client Installation Prerequisites

Use this reference when a skill needs to confirm that `dikw client` is
available before running commands.

## Required package

Install `dikw-core` from PyPI. It provides the `dikw` CLI used by every skill.
Any installer works — pick whichever matches your environment:

```bash
pip install dikw-core          # into the active venv (simplest)
pipx install dikw-core         # isolated, on PATH
uv tool install dikw-core      # isolated, on PATH (uv users)
```

Python `>=3.12` is required.

## Optional import converters

Converters are plugins that `dikw client` discovers **in-process**, so they must
live in the **same environment as `dikw-core`** — not as a separate isolated
tool. Install only when importing matching non-Markdown material:

```bash
# Same venv as dikw-core (the pip install above):
pip install dikw-converter-mineru
pip install dikw-converter-epub

# If dikw-core was installed as an isolated tool, inject into that same env:
uv tool install dikw-core --with dikw-converter-mineru   # uv
pipx inject dikw-core dikw-converter-mineru              # pipx
```

Use `dikw-converter-mineru` (engine `mineru`) for MinerU-backed conversion of
PDF and office documents (`.pdf`, `.docx`, `.pptx`, `.xlsx`, …). Use
`dikw-converter-epub` (engine `epub`) for EPUB → Markdown. A bare
`uv tool install dikw-converter-*` creates an isolated tool whose plugin
`dikw client` cannot discover.

## Prerequisite commands outside this skill set

Root commands are setup context, not owned skill commands:

```bash
dikw init ./my-base --description "agent knowledge base"
dikw serve --base ./my-base
dikw auth status openai-codex --wiki ./my-base
```

After setup, use only `dikw client *` commands from these skills.
