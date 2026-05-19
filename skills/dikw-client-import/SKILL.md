---
name: dikw-client-import
description: Import local source material into a dikw-core base through `dikw client import`. Use when an agent needs to pre-flight Markdown files or directories, import local sources into the server's `sources/` tree, or use optional PyPI converter packages such as `dikw-converter-mineru` or `dikw-converter-epub` for non-Markdown inputs.
---

# DIKW Client Import

Use this skill to move local source material into the server-bound
`<base>/sources/` tree. Import only stages source packages; run curation
commands later to index them.

## Prerequisites

Read `../../references/installation.md` when the CLI or converter availability
is unclear. `dikw-core` must be installed from PyPI and provide `dikw`.

Install optional converters only when needed:

```bash
uv tool install dikw-converter-mineru
uv tool install dikw-converter-epub
```

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
