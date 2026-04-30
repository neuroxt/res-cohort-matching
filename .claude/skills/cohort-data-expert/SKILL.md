---
name: cohort-data-expert
description: Use when the user asks about NeuroXT cohort data — ADNI / OASIS3 / A4 / LEARN file layouts, CSV columns, join keys, demographics encodings, matching/extraction logic, or which file lives where on NFS. Grounded in res-cohort-matching/docs/. Triggers include "OASIS3 데이터", "ADNI 매칭 로직", "A4 BASELINE.csv", "코호트 컬럼 / CSV / 파일", "어디에 어떤 csv가", "이 매칭 어떻게 했지", "what CSVs", "demographics columns", "join keys", "cohort file", and similar.
---

# Cohort Data Expert

In-house NeuroXT skill for answering cohort-data questions inside the **res-cohort-matching** repo. Routes simple lookups inline and spawns a specialist subagent for deeper work.

## When to use this skill

Activate as soon as the user asks anything about cohort data:

- "What CSVs does OASIS3 have, and which one has demographics?"
- "OASIS3 demographics CSV에 어떤 컬럼 있어? race 인코딩도."
- "A4 BASELINE.csv 369컬럼 중 imaging 관련은?"
- "예전 ADNI 매칭 로직 어떻게 돌렸지?"
- "Compare A4 vs OASIS3 visit structure."
- "어떤 파일이 NFS의 어디에 있는지 정리해줘."

If the question is "where does this column come from" / "what cohort docs do we have" / "which CSV / file / column / encoding / join", this skill applies.

## Decision: answer inline vs spawn subagent

### Answer inline (fast path) when:
- The question is about a **single cohort** and likely covered by **1–2 docs**.
- The user wants a quick lookup ("what columns are in X CSV?", "where is file Y?", "what's the join key for Z?").
- No source-code tracing or raw-CSV verification is needed.

Inline workflow:
1. `Read docs/README.md` for orientation (lists all cohort docs and what each covers).
2. `Read` the 1–2 most relevant cohort docs (e.g., `docs/oasis3/demographics.md`).
3. Answer with citations. Always quote column names / value codes / paths verbatim from the docs — never invent.

### Spawn the `cohort-data-expert` subagent when:
- **Cross-cohort comparison** — "compare ADNI vs OASIS3 demographics", "which cohorts have Tau PET?".
- **Matching / extraction logic code tracing** — "how did we match DICOMs?", "what's the BASELINE.csv build pipeline?".
- **ADNI questions** — there are no `docs/adni/` files; the agent has to trace `src/adni/` and `vendor/ADNIMERGE2/` directly. The subagent has the right tools and discipline for this.
- **Verification against a raw CSV/PDF** is needed (the subagent will ask the user permission before reading raw data).
- **5+ files** would need to be read to answer well.
- **Repeat / batch** — multiple related questions in one go.

How to invoke:

Spawn the `cohort-data-expert` subagent via the Agent tool. Brief it like a colleague who hasn't seen this conversation — include the verbatim user question, which cohort(s) are in scope, and the desired output shape (bullets, comparison table, file path list, etc.). The subagent owns its own context window, citation discipline, and ADNI fallback logic, so do not pre-summarize cohort docs in the prompt; just hand off the question and let it work.

## Output rules (apply whether answering inline or summarizing the subagent's result)

1. **Always cite sources.** Every fact gets a file reference (`docs/oasis3/demographics.md`, `src/adni/matching/matching.py`).
2. **Quote, don't invent.** Column names, value encodings, and row counts must come from docs or code. If something isn't documented, say "not currently documented in `docs/`" — never guess.
3. **Surface NFS paths verbatim** as written in the docs (e.g., `/Volumes/nfs_storage/OASIS3/ORIG/DEMO/`). Add one note: *"Replace the mount root with your local environment's mount (Windows `Z:\1_combined\`, Linux `/mnt/nfs/`, etc.)."*
4. **Don't read raw CSVs without permission.** If verification requires it, ask first.

## What this skill does *not* do

- Does not answer general Python / pipeline / install / pyproject questions — that's a different scope.
- Does not write or modify cohort docs. (If the user wants new docs created, hand back to a normal coding session.)
- Does not load entire CSVs into context. `head -n 1` for headers and `wc -l` for row counts are sufficient.

## Quick map (defer to `docs/README.md` for the maintained list)

- **OASIS3** — `docs/oasis3/` (8 docs)
- **A4 / LEARN** — `docs/a4/` (8 docs)
- **ADNI / ADNI 4** — no `docs/adni/` yet; trace `src/adni/`, `src/adni/extraction/`, `src/adni/matching/`, `vendor/ADNIMERGE2/`
- **NACC** — planned, not implemented
