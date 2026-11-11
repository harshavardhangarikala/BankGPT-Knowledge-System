@echo off
setlocal
cd /d "%~dp0"
echo ============================================
echo BankGPT Public Assessment - All Five Snapshots
echo ============================================
python harness\run_eval.py --submission submission --eval eval\public_eval.jsonl
if errorlevel 1 (
 echo.
 echo ERROR: The evaluation failed. Verify Python is installed.
) else (
 echo.
 echo Done. Report saved to results\report.json
)
pause
