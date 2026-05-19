# DIKW Client Installation Prerequisites

Use this reference when a skill needs to confirm that `dikw client` is
available before running commands.

## Required package

Install `dikw-core` from PyPI. It provides the `dikw` CLI used by every skill:

```bash
uv tool install dikw-core
```

Python `>=3.12` is required.

## Optional import converters

Install converters only when importing matching non-Markdown source material:

```bash
uv tool install dikw-converter-mineru
uv tool install dikw-converter-epub
```

Use `dikw-converter-mineru` for MinerU-backed document conversion such as PDF
or office-document workflows supported by that plugin. Use
`dikw-converter-epub` for EPUB to Markdown conversion.

## Prerequisite commands outside this skill set

Root commands are setup context, not owned skill commands:

```bash
dikw init ./my-base --description "agent knowledge base"
dikw serve --base ./my-base
dikw auth status openai-codex --wiki ./my-base
```

After setup, use only `dikw client *` commands from these skills.
