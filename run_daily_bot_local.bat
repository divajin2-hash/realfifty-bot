@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ==============================================
echo [RealFifty] Scheduled Daily PropTech Bot Start
echo ==============================================

:: 파이프라인 마스터 스크립트 실행
python 32_master_daily_run.py

if %errorlevel% neq 0 (
    echo [ERROR] 파이프라인 실행 중 오류가 발생했습니다.
    exit /b %errorlevel%
)

:: Vercel 자동 배포를 위한 Git 자동 커밋 및 푸시
echo [RealFifty] Vercel 배포를 위한 DB 자동 커밋 및 푸시...
git add web/src/data/kb50_stats.json
git diff --quiet && git diff --staged --quiet || (git commit -m "[Daily Bot] 자정 자동 스크래핑 및 DB 갱신 (로컬 PC 스케줄러)" && git push)

echo ==============================================
echo [RealFifty] Daily PropTech Bot 완료!
echo ==============================================
