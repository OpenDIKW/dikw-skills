---
name: dikw-client-import
description: Import local source material into a dikw-core base through `dikw client import`. Use when an agent needs to pre-flight Markdown files or directories, import local sources into the server's `sources/` tree, or use optional PyPI converter packages such as `dikw-converter-mineru` or `dikw-converter-epub` for non-Markdown inputs.
---

# DIKW Client Import

Use this skill to move local source material into the server-bound
`<base>/sources/` tree. Import only stages source packages; run curation
commands later to index them.

## Prerequisites

`dikw-core` must be installed from PyPI and provide the `dikw` CLI. Install
the CJK extra by default for Chinese/CJK bases (`pip install
"dikw-core[cjk]"`, or `pipx`/`uv tool` if you prefer an isolated tool).

Converters are plugins `dikw client` discovers **in-process**, so install them
into the **same environment as `dikw-core`** — only when actually needed:

```bash
# Same venv as dikw-core:
pip install dikw-converter-mineru     # engine "mineru": .pdf/.docx/.pptx/.xlsx
pip install dikw-converter-epub       # engine "epub": .epub

# If dikw-core is an isolated tool, inject into that env instead:
uv tool install "dikw-core[cjk]" --with dikw-converter-mineru   # uv
pipx inject dikw-core dikw-converter-mineru              # pipx
```

A bare `uv tool install dikw-converter-*` creates a separate isolated tool whose
plugin `dikw client` cannot see — that is why it must share dikw-core's env.

## Import SOP

Import Markdown files or directories:

```bash
dikw client import ./inbox
dikw client import ./note.md
```

Import converter-backed non-Markdown files:

```bash
dikw client import ./paper.pdf --converter mineru
dikw client import ./book.epub --converter epub
```

The importer pre-flights local files before uploading: frontmatter parse,
non-empty body checks, asset existence checks, and package integrity. Local
pre-flight failures exit before bytes are sent to the server.

The committed / rejected summary prints as JSON by default; add `--format table`
for the human-readable summary.

## After Import

After successful import, use `dikw-client-curate` to refresh the searchable
index:

```bash
dikw client ingest --wait --plain
dikw client ingest --no-embed --wait --plain
```

Do not treat import as indexing. It commits well-formed packages into
`sources/`; `ingest` chunks and optionally embeds them.

## Failure Handling

- Exit `2` usually means local user input was invalid before upload.
- A response with `rejected` packages means some packages failed server-side
  validation or commit; report the rejected package ids and reasons.
- Do not install converters speculatively. Install `dikw-converter-mineru` or
  `dikw-converter-epub` only for formats the user actually imports.
