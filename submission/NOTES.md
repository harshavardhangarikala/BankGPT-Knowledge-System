# Snapshot-aware credit union knowledge system

`solution.py` exports `build()` with the three required methods: `ingest`, `answer`, and `conflicts`. It uses only the Python standard library, has no API keys, makes no live website requests, and never includes the site's snapshot data in its source code.

## Approach

Snapshots are indexed separately and retained chronologically. For pages absent from a later crawl, the last observed copy is retained as a fallback (excluding time-limited promotions); explicit as-of questions still select their historical snapshot. Each page is broken into headings, readable paragraphs, and table rows. A sparse, deterministic BM25-style inverted index supports fast topical retrieval. For financial rates, the system parses markdown tables into facts with **product, term, balance tier, measurement type (APR, APY, or dividend rate), value, source URL, and snapshot ID**. Specific mortgage amounts, model-year ranges, jumbo versus standard certificates, and rate versus APY are treated as distinct qualifiers, not conflicts.

An `as_of` parameter selects the newest snapshot dated on or before the requested day; without it, the latest ingested snapshot is used. Queries for numeric products use exact tier/term matches on the strongest source (official product tables), rather than a calculator or old blog post. For general questions, source-ranked passages from the selected snapshot provide a short answer and a supporting quote. If a rate or required detail is missing, the system returns a non-confident refusal instead of inventing a value.

`conflicts()` looks for changes to the same qualified table fact across snapshots, returns competing values and citations, and resolves current facts to the last observed snapshot. A source-priority check also detects competing illustrative calculator values in some cases. In real usage, an as-of answer remains historically grounded even when a fact has since changed. Identical questions and data always lead to identical answers.

## Run

From the participant kit root:

```bash
python harness/run_eval.py --submission submission --eval eval/public_eval.jsonl
```

Nothing should be installed from `requirements.txt`, because it has no dependencies. The evaluation harness unpacks the supplied snapshots locally. Neither those snapshots nor API keys should be committed to a public repository.

## Limitations

Passage extraction without a generative model can be less natural for unstructured complex questions. Temporal claims embedded inside undated legacy pages can remain ambiguous. The model intentionally prioritizes precise citations and abstention over unsupported guesses; future improvements could add offline semantic reranking, entity-specific validators, and a cross-page fact reconciliation graph.
