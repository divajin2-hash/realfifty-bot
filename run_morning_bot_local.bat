@echo off
cd /d "D:\appmaking\kb50_mdd"
echo Running Morning News FactCheck Bot...
call F:\anacon\Scripts\activate.bat
call conda activate proptech_env

echo "1. Run morning python pipeline (Scraping + Gemini Fact Check)"
python 33_morning_news_run.py
IF %ERRORLEVEL% NEQ 0 (
    echo "Python script failed."
    exit /b %ERRORLEVEL%
)

echo "2. Push output JSON to Web/Vercel"
git add web/src/data/factcheck_news.json
git commit -m "bot: update morning news factcheck"
git push

echo "Successfully completed Morning News update!"
