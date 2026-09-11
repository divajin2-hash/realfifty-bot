import os
import sys

print("======================================================")
print(" 🏙️ RealFifty 매일 자동화 파이프라인 (Master Cron) 시작 ")
print("======================================================")

# Forward execution to the actual working master pipeline
res = os.system(f"{sys.executable} 32_master_daily_run.py")

if res != 0:
    print("\n[ERROR] 파이프라인 실행 중 오류가 발생했습니다.")
    sys.exit(1)

print("\n[SUCCESS] 파이프라인이 정상 종료되었습니다.")
