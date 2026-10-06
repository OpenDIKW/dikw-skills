---
name: dikw-client-retrieve
description: Retrieve grounded evidence from a running dikw-core server with read-only `dikw client` commands, then compose the answer yourself. Use when an agent needs chunks, page bodies, K-layer link neighbours, source provenance, the full base graph, or assets through `dikw client retrieve`, `dikw client pages list`, `dikw client pages get`, `dikw client pages links`, `dikw client pages provenance`, `dikw client graph get`, or `dikw client assets get`.
---

# DIKW Client Retrieve

Use this skill for read-only knowledge access.
`dikw-core` returns evidence. It does not call an LLM and does not write the answer. You compose the final answer from the evidence.

## Retrieval SOP

1. If the server state is unknown, probe it first: `dikw client health`.
2. Retrieve chunks. Add `--plain` whenever you parse stdout, so the status banner cannot break the JSON:

   ```bash
   dikw client retrieve "your question" --plain
   dikw client retrieve "your question" --limit 10 --plain
   ```

   The output is JSON with `chunks` and `page_refs`. JSON is the default, so do not add `--format json`.
3. Look further before you answer:
   - If the chunks are thin or off-topic, retrieve again with one or two other phrasings: synonyms, the key entity name, or the other language of a bilingual base.
   - If a chunk is too narrow, read its whole page with `pages get`.
   - If the question is about relations, expand one hop with `pages links`.
4. Answer from the evidence only. Cite the page `path` for each claim.

Done when each claim in your answer cites a retrieved path, or you have said what the base does not contain.

## Paths

- D layer (sources): `sources/...`
- K layer (generated knowledge): `knowledge/<category>/<slug>.md`. The default categories are `entity`, `concept`, and `note`; a base can declare its own.
- W layer (hand-written wisdom): `wisdom/[<author>/]<slug>.md`

## Page and graph expansion

Read full pages from the paths in `page_refs`:

```bash
dikw client pages list
dikw client pages list --layer source
dikw client pages get sources/notes/alpha.md
dikw client pages get knowledge/concept/neural-network.md
```

`--layer` takes `source`, `knowledge`, or `wisdom`.

Expand K-layer context through page links. The output has `outgoing` and `incoming` edges:

```bash
dikw client pages links knowledge/concept/neural-network.md
dikw client pages links knowledge/concept/neural-network.md --direction out --limit 20
```

Fetch the whole base graph when global connectivity matters. It returns `nodes`, `edges`, `unresolved` (broken wikilinks), and `stats`:

```bash
dikw client graph get
dikw client graph get --no-active
```

`--no-active` returns only deactivated documents instead of active ones.

Fetch an image or other asset only to a local file. Stdout carries a JSON envelope (`asset_id`, `path`, `bytes`):

```bash
dikw client assets get <asset_id> --output ./assets/<asset_id>.png
```

## Page provenance

`pages provenance` traces the attribution edge between a K-layer page and the D-layer sources it was synthesised from.
Use it when you must cite the sources of a page, or find which K pages a source has fed:

```bash
dikw client pages provenance knowledge/concept/neural-network.md
dikw client pages provenance sources/notes/foo.md --direction in
dikw client pages provenance knowledge/concept/neural-network.md --direction out --limit 20 --format table
```

Default JSON shape:

```json
{
  "path": "knowledge/concept/neural-network.md",
  "derived_from": [
    {"source_path": "sources/notes/foo.md", "doc_id": "...", "title": "Foo", "resolved": true}
  ],
  "derived_pages": [
    {"doc_id": "...", "path": "knowledge/concept/deep-learning.md", "title": "Deep Learning"}
  ]
}
```

- Unlike `pages links`, dangling references stay in the output with `resolved: false`. That is how you find a `sources:` entry that points at a source that is no longer indexed.
- `--direction out` returns only `derived_from`. `--direction in` returns only `derived_pages`. The default returns both.

## Grounding rules

- Prefer chunk text for direct grounding.
- Use `pages get` when a chunk is too narrow or the user asks about a whole page.
- Use `pages links` for one-hop K-layer context. Use `graph get` for global graph analysis.
- To cite the sources of a K page, use `pages provenance` for the real `derived_from` list. Do not parse the page's front matter yourself.
- Mark each claim that the evidence does not support. Say which queries and pages you checked.
- Never claim that `retrieve` called an LLM. It returns chunks and page refs only.
- If a path returns 404, run `dikw client pages list`. The file can exist on disk but not be indexed yet.

## Shared options

- `--server` / `--token` default to `$DIKW_SERVER_URL` (else `http://127.0.0.1:8765`) and `$DIKW_SERVER_TOKEN` (else client config).
- Data-returning commands here print JSON by default. Add `--format table` only for a human, where supported.
- Add `--plain` to `retrieve` whenever stdout is parsed.
