@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if not exist logs mkdir logs
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set LOG_FILE=logs\run_%TS%.log
powershell -NoProfile -Command ^
  "[Console]::OutputEncoding=[Text.Encoding]::UTF8;" ^
  "[Console]::InputEncoding=[Text.Encoding]::UTF8;" ^
  "$OutputEncoding=[Text.Encoding]::UTF8;" ^
  "uv run src/main.py 2>&1 | Tee-Object -FilePath '%LOG_FILE%' "
pause