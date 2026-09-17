import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_script(script_name, *args):
    print(f"\n{'='*50}\n> RUNNING: {script_name}\n{'='*50}")
    # Using python module execution to stay in the same env
    res = subprocess.run([sys.executable, str(Path(__file__).parent / "pipeline" / script_name), *args]).returncode
    if res != 0:
        print(f"FAILED at {script_name}. Stop pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    # Ensure we are in root dir (kb50_mdd)
    
    # 1. Update MOTIE recent deals (This Month & Last Month)
    # [PRO ?곸슜] 吏곴굅???꾪꽣 諛??뚯닔??硫댁쟻 蹂댁〈, ?낆＜沅?遺꾩뼇沅??숈떆 ?쒗쉶
    # Official source refresh runs after asking-price collection below.

    # 2. Update Naver lowest ask prices
    # [PRO ?곸슜] ?먯옄 ?⑥쐞 ?멸? ?ㅽ겕?섑띁 (理쒖?媛 100% ?섏쭛?섏뿬 raw_daily_asks.json ?앹꽦)
    os.chdir(Path(__file__).resolve().parent)
    run_script("11_api_scraper_v2.py")
    run_script("daily_type_matching.py", "--asks", f"pipeline/raw_daily_asks_{datetime.now():%Y-%m-%d}.json")
    os.environ["RTMS_VERIFIED_FILE"] = str(Path("pipeline/rtms_recheck/verified_full.json").resolve())
    
    # 3. ?ㅼ씠踰??섏쭛?뚯씪 + 援?넗遺 ?뚯씪 寃고빀 諛?MDD(pyeong_stats) ?앹꽦 泥섎━湲?
    run_script("20_mdd_bridge.py")
    
    # 4. Re-build the JSON DB that the frontend reads
    run_script("19_build_json_db.py")
    
    # 5. Take a snapshot
    run_script("30_daily_snapshot.py")
    
    # 6. Build chart data
    run_script("36_build_chart_data.py")
    
    # 7. Build Macro Indices (Transaction & Volume)
    run_script('36_build_macro_index.py')
    run_script('38_build_tx_index.py')
    run_script('45_news_crawler.py')
    
    # 8. Generate AI Daily Report and Fact Check JSON
    run_script('40_ai_reporter.py')
    run_script('50_persona_comment_bot.py')

    print("\n??All daily master bot scripts executed successfully!")

    # 8. Send Telegram Notification
    run_script("35_telegram_notify.py")
