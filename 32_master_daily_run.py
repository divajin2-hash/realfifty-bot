import os
import sys

def run_script(script_name):
    print(f"\n{'='*50}\n🚀 RUNNING: {script_name}\n{'='*50}")
    # Using python module execution to stay in the same env
    res = os.system(f"python pipeline/{script_name}")
    if res != 0:
        print(f"❌ Failed at {script_name}. Stop pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure we are in root dir (kb50_mdd)
    # The GH Action runs from the root of the repo
    
    # 1. Update MOTIE recent deals (This Month & Last Month)
    run_script("31_daily_rtms.py")

    # 2. Update Naver lowest ask prices and calc MDD 
    run_script("18_naver_batch.py")
    
    # 3. Re-build the JSON DB that the frontend reads
    run_script("19_build_json_db.py")
    
    # 4. Take a snapshot of the newly generated JSON and save it to Daily History DB
    run_script("30_daily_snapshot.py")
    
    print("\n✅ All daily master bot scripts executed successfully!")
