import os
import subprocess
from datetime import datetime, timedelta

def run():
    start_date = datetime(2026, 7, 27)
    end_date = datetime(2026, 8, 7)
    
    current_date = start_date
    last_available_file_date = "2026-07-27"
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        raw_file = f"pipeline/raw_daily_asks_{date_str}.json"
        
        # Check if raw file exists
        if os.path.exists(raw_file):
            print(f"\n[{date_str}] Found raw file. Using it.")
            used_date = date_str
            last_available_file_date = date_str
        else:
            print(f"\n[{date_str}] ⚠️ Raw file missing. Forward-filling with {last_available_file_date}.")
            # Copy previous available raw_daily_asks over to this missing date
            src_file = f"pipeline/raw_daily_asks_{last_available_file_date}.json"
            if os.path.exists(src_file):
                import shutil
                shutil.copy2(src_file, raw_file)
                used_date = date_str
            else:
                print("FATAL: Source file for forward fill missing.")
                break

        print(f"🔄 Rebuilding kb50_stats.json for {used_date}...")
        subprocess.run(["python", "pipeline/19_build_json_db.py", used_date], check=True)
        
        print(f"🔄 Pushing daily snapshot to Supabase for {used_date}...")
        subprocess.run(["python", "pipeline/30_daily_snapshot.py", used_date], check=True)
        
        current_date += timedelta(days=1)
        
    print("\n🎉 Backfill Complete! Rebuilding final macro indices...")
    subprocess.run(["python", "pipeline/36_build_macro_index.py"], check=True)
    subprocess.run(["python", "pipeline/37_build_volume_index.py"], check=True)
    subprocess.run(["python", "pipeline/38_build_tx_index.py"], check=True)
    print("ALL DONE. Time-series restored.")

if __name__ == "__main__":
    run()
