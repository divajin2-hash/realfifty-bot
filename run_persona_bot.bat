@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ==============================================
echo [RealFifty] AI Persona Comment Bot Start
echo ==============================================

cd pipeline
python 50_persona_comment_bot.py

if %errorlevel% neq 0 (
    echo [ERROR] Bot script failed.
    exit /b %errorlevel%
)

echo ==============================================
echo [RealFifty] AI Persona Comment Bot Finished!
echo ==============================================
