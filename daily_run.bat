@echo off
chcp 65001
echo ======================================================
echo RealFifty 자동화 파이프라인 시작
echo ======================================================
cd /d %~dp0
python master_daily_cron.py

echo.
echo ======================================================
echo 프론트엔드 최신 데이터 자동 배포 (GitHub Push - Vercel)
echo ======================================================
git add .
git commit -m "Auto-update: Daily Market Snapshot & Indices"
git push

echo.
echo 모든 작업이 완료되었습니다! 창을 닫아주세요.
pause
