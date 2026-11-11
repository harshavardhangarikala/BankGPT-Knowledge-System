# Knowledge system that knows what's true now

A self-contained, offline Python solution to the time-versioned credit-union
knowledge-system engineering assignment. Built for Python 3.9–3.11+, using **only
the standard library**; no API key, LLM subscription, internet connection or
remote database is required.

## What it does

- `ingest(snapshot)` parses successive website snapshots in chronological order.
- `answer(question, as_of=None)` finds the latest valid source for current or
  historical questions and returns an answer, citations and confidence.
- `conflicts()` detects changes to the *same* qualified financial facts and
  indicates the selected resolution, with sources from each snapshot.
- Handles rate tables with different terms and balance ranges, standard versus
  jumbo certificates, APR versus APY, source authority and explicit refusals.
- Indexes remaining passages for sourced non-numeric answers.

The public evaluator score for this version, using the original five supplied
snapshots, is **0.9690** across the 40 public questions. The synthetic harness
self-test including conflict validation scores **1.0000**. These are practice
scores; performance on hidden questions is not guaranteed.

## Project layout

```text
submission/
    solution.py         # build(), ingest(), answer(), conflicts()
    requirements.txt    # no third-party dependencies
    NOTES.md            # approach, chronology, rules, limitations
harness/                # original evaluation contract and scorer
    selftest/           # synthetic test data (not the credit-union snapshots)
eval/public_eval.jsonl  # supplied practice question set
snapshots/README.md     # notes on keeping website data local/private
tests/test_contract.py  # independent contract and behavior smoke tests
.gitignore             # excludes original website downloads and credentials
```

## Run in a clean environment

1. Create a Python 3.11 virtual environment if desired. No package installation
   is needed because `requirements.txt` has no dependencies.
2. Copy the original participant kit's **five snapshot zip files** to
   `snapshots_zip/` locally. Do not commit these files to GitHub.
3. Run from this directory:

```bash
python harness/run_eval.py --submission submission --eval eval/public_eval.jsonl
python harness/run_eval.py --submission submission --snapshots harness/selftest/snapshots --eval harness/selftest/eval.jsonl --conflicts-gold harness/selftest/conflicts_gold.json
python -m unittest discover -s tests -v
```

The supplied harness automatically unpacks `snapshots_zip/*.zip` into
`snapshots/`, which is also Git-ignored. For independent tests, the synthetic
self-test runs without any private snapshot files.

## Submission steps

Push this directory to a **public GitHub repository**, verify no proprietary
snapshot data or secret keys are tracked, and then email the repository URL and
the exact commit SHA to `assignments@interface.ai` as instructed in the invitation.

See `submission/NOTES.md` for details about source ranking, temporal queries,
precise tiers and conflict detection.
