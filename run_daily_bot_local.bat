@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ==============================================
echo [RealFifty] Scheduled Daily PropTech Bot Start
echo ==============================================

python 32_master_daily_run.py
python pipeline/40_market_report_agent.py

if %errorlevel% neq 0 (
    echo [ERROR] Python script failed.
    exit /b %errorlevel%
)

echo [RealFifty] Git commit and push for Vercel deploy...
git add web/
git diff --quiet && git diff --staged --quiet || (git commit -m "[Daily Bot] Auto-update DB" && git push)

echo ==============================================
echo [RealFifty] Daily PropTech Bot Finished!
echo ==============================================
