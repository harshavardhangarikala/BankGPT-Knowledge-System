# START HERE — Local assessment, with all five website snapshots

This folder contains **the supplied private snapshot ZIPs** alongside the
solution and the original scoring harness. It is for **LOCAL EVALUATION ONLY**.
**DO NOT** upload this archive, its `snapshots_zip/` folder, or the extracted
`snapshots/` files to any public GitHub repository.

## VS Code (Windows PowerShell)

1. Extract the archive.
2. Open **BankGPT_Knowledge_Assessment** (the folder that contains `harness`,
   `submission`, and `snapshots_zip`) in VS Code, NOT its parent folder.
3. Run in the terminal:

```powershell
python harness/run_eval.py --submission submission --eval eval/public_eval.jsonl
```

On first run, the provided harness automatically unpacks five dated ZIPs and
prints five `ingest ...` lines (one per snapshot). It may take a little longer.
The output ends with the question score and saves `results/report.json`.

If your terminal opens one folder above the project, first run:

```powershell
cd .\BankGPT_Knowledge_Assessment
```

To run the independent synthetic self-test, use:

```powershell
python harness/run_eval.py --submission submission --snapshots harness/selftest/snapshots --eval harness/selftest/eval.jsonl --conflicts-gold harness/selftest/conflicts_gold.json --out results/selftest
```

Or double-click `RUN_PUBLIC_EVALUATION.bat` from File Explorer.

## Public GitHub submission

Use the **separate GitHub-ready ZIP**, which intentionally omits the supplied
website data. `snapshots_zip/` and `snapshots/` are excluded by `.gitignore`.
Share only your source code, supplied harness and public evaluation materials,
not the website snapshots.

The earlier 9.3% score with `ingest_seconds: 0.0` happened because no original
website snapshots were present; the harness then evaluated an empty system.

The previously verified practice result with all five supplied snapshots was
0.9690 accuracy on the public 40-question set. This is not a guaranteed score
on any private/hidden evaluation.
