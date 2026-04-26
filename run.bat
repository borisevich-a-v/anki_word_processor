@echo off
set PYTHONUTF8=1
if not exist logs mkdir logs
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set LOG_FILE=logs\run_%TS%.log
uv run src/main.py 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%'"