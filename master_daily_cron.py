import subprocess
import sys
import datetime
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def run_step(script_name):
    print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 실행 중: {script_name}")
    try:
        # Run the script and stream output
        result = subprocess.run([sys.executable, f"pipeline/{script_name}"], check=True, text=True, capture_output=True, encoding='utf-8')
        print(result.stdout)
        print(f"✅ 완료: {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 에러 발생 ({script_name}):")
        print(e.stdout)
        print(e.stderr)
        print("\n중단합니다. 파이프라인이 완전하게 끝나지 않았습니다.")
        sys.exit(1)

def main():
    print("======================================================")
    print(" 🏙️ RealFifty 매일 자동화 파이프라인 (Master Cron) 시작 ")
    print("======================================================")
    
    # 1. 국토부 실거래가 크롤링 및 DB 업데이트
    run_step("31_daily_rtms_pro.py")
    
    # 2. 네이버 최저호가 크롤링 (raw_daily_asks 생성)
    run_step("32_daily_naver_pro.py")
    
    # 3. [핵심] 초정밀 소수점 매칭 및 통계 JSON 빌드 (kb50_stats.json)
    run_step("19_build_json_db.py")
    
    # 4. 일간 스냅샷 (대표 평형) DB 기록 (daily_history)
    run_step("30_daily_snapshot.py")
    
    # 5. 차트 데이터 및 매크로 인덱스 빌드 (프론트엔드 연동)
    run_step("36_build_chart_data.py")
    run_step("36_build_macro_index.py")
    run_step("37_build_volume_index.py")
    run_step("38_build_tx_index.py")
    
    # 6. 보고서 생성 및 텔레그램 발송
    run_step("35_telegram_notify.py")
    
    print("======================================================")
    print(" 🎉 모든 파이프라인이 성공적으로 완료되었습니다! (Git Push 수행 필요) ")
    print("======================================================")

if __name__ == "__main__":
    main()
