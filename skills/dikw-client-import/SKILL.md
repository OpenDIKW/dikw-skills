---
name: dikw-client-import
description: Import local source material into a dikw-core base through `dikw client import`. Use when an agent needs to pre-flight Markdown files or directories, import local sources into the server's `sources/` tree, or use optional PyPI converter packages such as `dikw-converter-mineru` or `dikw-converter-epub` for non-Markdown inputs.
---

# DIKW Client Import

Use this skill to move local source material into the server's `<base>/sources/` tree.
Import only stages source packages. Run `ingest` afterwards to index them.

## Prerequisites

- `dikw-core` is installed from PyPI and provides the `dikw` CLI. Install the CJK extra by default for Chinese/CJK bases (`pip install "dikw-core[cjk]"`, or `pipx` / `uv tool` for an isolated tool).
- Converters are plugins that `dikw client` loads **in-process**. Install them into the **same environment as `dikw-core`**, and only when the user imports that format:

```bash
# Same venv as dikw-core:
pip install dikw-converter-mineru     # engine "mineru": .pdf/.docx/.pptx/.xlsx
pip install dikw-converter-epub       # engine "epub": .epub

# If dikw-core is an isolated tool, inject into that env instead:
uv tool install "dikw-core[cjk]" --with dikw-converter-mineru   # uv
pipx inject dikw-core dikw-converter-mineru              # pipx
```

A bare `uv tool install dikw-converter-*` creates a separate isolated tool. `dikw client` cannot see its plugin.

## Import SOP

Import only what the user asked for. If the user named a directory but not the files, list the files it will import and confirm before you run it. Import writes into the server's `sources/` tree.

1. Import Markdown files or directories:

   ```bash
   dikw client import ./inbox
   dikw client import ./note.md
   ```

2. Import a non-Markdown file through an installed converter. The importer picks the converter by file extension. `--converter` overrides that choice for one call:

   ```bash
   dikw client import ./paper.pdf --converter mineru
   dikw client import ./book.epub --converter epub
   ```

3. Read the `committed` / `rejected` summary. It prints as JSON by default; add `--format table` for a human.

Done when every package is committed, or you have reported each rejected package with its reason.

Each Markdown file becomes one package together with the assets (images, PDFs) that it embeds.
The importer pre-flights the files locally before it uploads: front matter parse, asset existence, non-empty body, and no orphan asset.
A local pre-flight failure exits before any bytes leave the machine.

## After import

Import is not indexing. It commits well-formed packages into `sources/`; `ingest` chunks and optionally embeds them.
Use `dikw-client-curate` to refresh the index. The agent-friendly default is async:

```bash
dikw client ingest
dikw client ingest --no-embed
```

Capture the returned `task_id` and follow it with `dikw-client-utils`.
Use `--wait --plain` only when the user wants the ingest report from this command.

## Failure handling

- Exit `2` usually means the local input was invalid before upload. Report the file and the pre-flight error.
- The command exits `1` when the server rejects any package. That is not a crash: read the `rejected` list.
- `rejected` packages failed server-side validation or commit. Report each package id and its reason.
- Do not install converters speculatively. Install `dikw-converter-mineru` or `dikw-converter-epub` only for formats the user actually imports.
- `dikw client import` is different from `dikw auth import`, which loads OAuth credentials.
