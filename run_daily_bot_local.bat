@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ==============================================
echo [RealFifty] Scheduled Daily PropTech Bot Start
echo ==============================================

REM The master pipeline generates the daily report once.
python 32_master_daily_run.py

if %errorlevel% neq 0 (
    echo [ERROR] Python script failed.
    exit /b %errorlevel%
)

echo [RealFifty] Git commit and push for Vercel deploy...
REM Refuse to combine an existing staged change with an automated data commit.
git diff --cached --quiet
if errorlevel 1 exit /b 1
git add -- web/src/data/kb50_stats.json web/src/data/macro_index.json web/src/data/macro_tx_index.json web/src/data/daily_changes.json web/src/data/reports/ web/src/data/ai-talk/ web/public/chart_data/
if errorlevel 1 exit /b 1
git diff --cached --quiet
if not errorlevel 1 goto publish
git commit -m "[Daily Bot] Update verified market data and AI research"
if errorlevel 1 exit /b 1
:publish
REM Fast-forward only: a remote conflict stops publication instead of overwriting it.
git push origin HEAD:main HEAD:v2-terminal-development
if errorlevel 1 exit /b 1

echo ==============================================
echo [RealFifty] Daily PropTech Bot Finished!
echo ==============================================
