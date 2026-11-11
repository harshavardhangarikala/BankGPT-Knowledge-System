# Viewing your five website snapshots in a browser

**Windows**: Extract the ZIP, open `BankGPT_Knowledge_Assessment`, and double-click **`START_WEB_DEMO.bat`**.

**VS Code terminal**: From `BankGPT_Knowledge_Assessment`, run:

```powershell
python web_demo.py
```

The browser should open automatically. If it does not, navigate to **http://127.0.0.1:8765**.

The local demo has three sections:

1. **Snapshot browser** – select any of the five crawl dates, search ~600–700 pages per snapshot, and view their preserved Markdown text and tables. Toggle between a formatted display and raw source Markdown. This is a *reconstruction from saved pages*, not the original fully interactive website.
2. **Ask BankGPT** – ask a question about the credit union. Choose the latest snapshot or a historical date. Results display confidence and source references.
3. **Conflicts** – inspect reported contradictions and explanations.

The first start extracts the five ZIP archives (if needed), then ingests the pages. No API key, installation, or internet connection is required. It runs only on your computer at **127.0.0.1**. Stop with **Ctrl+C**.

**Do not deploy this ZIP publicly or upload the supplied snapshots to GitHub.** The assignment prohibits redistributing the participant website snapshots. For a public code-only repo, remove `snapshots_zip/` and extracted snapshot data; `.gitignore` already excludes them.

If `Address already in use` appears, run `python web_demo.py --port 8766` and open `http://127.0.0.1:8766`.

To rerun the official public evaluation use:

```powershell
python harness/run_eval.py --submission submission --eval eval/public_eval.jsonl
```
