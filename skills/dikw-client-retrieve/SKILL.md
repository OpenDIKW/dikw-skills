---
name: dikw-client-retrieve
description: Retrieve grounded knowledge from a running dikw-core server using read-only `dikw client` commands. Use when an agent needs chunks, page bodies, wiki graph neighbours, full graph data, or assets through `dikw client retrieve`, `dikw client pages list`, `dikw client pages get`, `dikw client pages links`, `dikw client graph get`, or `dikw client assets get`.
---

# DIKW Client Retrieve

Use this skill for read-only knowledge access. `dikw-core` retrieves context; it
does not synthesize the final LLM answer. Compose the final answer in the agent
using retrieved chunks, pages, and graph context.

## Retrieval SOP

Probe first if server state is unknown:

```bash
dikw client health --format json
```

Retrieve chunks with parseable output:

```bash
dikw client retrieve "your question" --plain --format json
dikw client retrieve "your question" --limit 10 --plain --format json
```

Use `--plain` when stdout will be parsed. Without it, rich progress banners may
break JSON consumers.

## Page and graph expansion

Use page refs from retrieval output to read full pages:

```bash
dikw client pages list --format json
dikw client pages list --layer source --format json
dikw client pages get sources/notes/alpha.md
dikw client pages get wiki/Some-Page.md
```

Expand K-layer context through page links:

```bash
dikw client pages links wiki/Some-Page.md --format json
dikw client pages links wiki/Some-Page.md --direction out --limit 20 --format json
```

Fetch the whole base graph when global connectivity matters:

```bash
dikw client graph get
dikw client graph get --no-active
```

Fetch immutable media assets only to local files:

```bash
dikw client assets get <asset_id> --output ./assets/<asset_id>.png
```

## Grounding Rules

- Prefer chunk text for direct answer grounding.
- Use `pages get` when a chunk is too narrow or the user asks about a whole page.
- Use `pages links` for one-hop wiki context; use `graph get` for global graph
  analysis.
- Never claim `retrieve` called an LLM. It returns chunks and page refs only.
- If a page path 404s, run `dikw client pages list --format json`; the file may
  exist on disk but not be indexed yet.

Read `../../references/dikw-client-command-reference.md` for shared option
behavior.
