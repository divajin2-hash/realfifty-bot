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
    
    # 1. 아침 9시 최신 핫뉴스 스크래핑
    run_script('45_news_crawler.py')
    
    # 2. AI 팩트체크 리포트 (latest_news.json + kb50_stats.json 기반)
    run_script('41_ai_news_factcheck.py')

    print("\n✅ All morning news bot scripts executed successfully!")
