import os
import sys

def run_script(script_name):
    print(f"\n{'='*50}\n> RUNNING: {script_name}\n{'='*50}")
    # Using python module execution to stay in the same env
    res = os.system(f"python pipeline/{script_name}")
    if res != 0:
        print(f"FAILED at {script_name}. Stop pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    # Ensure we are in root dir (kb50_mdd)
    
    # 1. Update MOTIE recent deals (This Month & Last Month)
    # [PRO 적용] 직거래 필터 및 소수점 면적 보존, 입주권 분양권 동시 순회
    run_script("31_daily_rtms_pro.py")

    # 2. Update Naver lowest ask prices
    # [PRO 적용] 원자 단위 호가 스크래퍼 (최저가 100% 수집하여 raw_daily_asks.json 생성)
    run_script("10_full_pyeong_scraper.py")
    
    # 3. 네이버 수집파일 + 국토부 파일 결합 및 MDD(pyeong_stats) 생성 처리기
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

    print("\n✅ All daily master bot scripts executed successfully!")

    # 8. Send Telegram Notification
    run_script("35_telegram_notify.py")
