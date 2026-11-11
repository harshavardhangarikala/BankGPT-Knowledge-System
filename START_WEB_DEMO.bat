@echo off
cd /d "%~dp0"
echo Starting BankGPT offline website snapshot demo...
echo This serves only your computer at http://127.0.0.1:8765
python web_demo.py
if errorlevel 1 (
  echo.
  echo Unable to start. Try: py -3 web_demo.py
  pause
)
