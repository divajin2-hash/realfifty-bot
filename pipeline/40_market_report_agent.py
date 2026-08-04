import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_representative_stat(stats):
    if not stats:
        return None
    now = datetime.now().timestamp() * 1000
    
    scored_stats = []
    for s in stats:
        diff_days = 99999
        if s.get("recent_deal_absolute") and s["recent_deal_absolute"].get("date"):
            try:
                last_date = datetime.strptime(s["recent_deal_absolute"]["date"], "%Y-%m-%d").timestamp() * 1000
                diff_days = abs(now - last_date) / (1000 * 3600 * 24)
            except: pass
            
        mk = s.get("match_key_area", 0)
        dist84 = abs(mk - 84)
        is_alive = diff_days <= 365
        group_dist = 0 if 82 <= mk <= 85 else dist84
        
        s_copy = s.copy()
        s_copy["diff_days"] = diff_days
        s_copy["dist84"] = dist84
        s_copy["is_alive"] = is_alive
        s_copy["group_dist"] = group_dist
        scored_stats.append(s_copy)
        
    # Sort
    def sort_key(s):
        vol = s.get("max_month_volume", 0) or 0
        hp = s.get("highest_deal_price", 0)
        return (
            0 if s["is_alive"] else 1,
            s["group_dist"],
            -vol,
            -hp
        )
        
    scored_stats.sort(key=sort_key)
    return scored_stats[0]

def generate_market_report():
    if not GEMINI_API_KEY:
        print("Gemini API 키가 없습니다.")
        return
        
    db_path = os.path.join("web", "src", "data", "kb50_stats.json")
    if not os.path.exists(db_path):
        print("DB 파일이 없습니다.")
        return
        
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    summary_items = []
    total_drop_sum = 0
    drop_count = 0
    total_vol = 0
    
    for g in data:
        rep = get_representative_stat(g.get("stats", []))
        if not rep:
            continue
        
        hp = rep.get("highest_deal_price", 0)
        rp = 0
        if rep.get("recent_deal_absolute"):
            rp = rep["recent_deal_absolute"].get("price", 0)
        if not rp:
            rp = hp
            
        recent_drop = ((rp - hp) / hp * 100) if hp > 0 else 0
        mdd = ((rep.get("current_lowest_ask", 0) - hp) / hp * 100) if hp > 0 else 0
        
        drop_count += 1
        total_drop_sum += recent_drop
        total_vol += rep.get("month_volume", 0)
        
        summary_items.append({
            "name": g["complex"]["name"],
            "pyeong": rep["pyeong_name"],
            "mdd_rate": mdd,
            "recent_drop": recent_drop,
            "month_vol": rep.get("month_volume", 0),
            "lowest_ask": rep.get("current_lowest_ask", 0)
        })
        
    avg_drop = (total_drop_sum / drop_count) if drop_count > 0 else 0
    
    summary_items.sort(key=lambda x: x["mdd_rate"])
    top_drop = summary_items[:3]
    
    summary_items.sort(key=lambda x: x["month_vol"], reverse=True)
    top_vol = summary_items[:3]
    
    prompt = f"""너는 'RealFifty'의 수석 부동산 시황 특파원이야.
데이터는 팩트 기반으로 날카롭고 전문적으로 해석하되, 독자들이 읽을 때 지루하지 않게 아주 유쾌하고 친근한 동네 고수 형/누나 어투로 브리핑해줘. 
가끔 위트 있는 농담과 이모지(🔥, 🥶, 💸, 📈, 📉 등)를 적극적으로 사용해줘.

오늘의 분석 데이터:
- 조사 대상: 선도 아파트 총 {drop_count}개 단지 대표 평형
- 전체 평균 실거래가 하락률: {avg_drop:.2f}%
- 최근 한 달간 전체 거래량: {total_vol}건

- 🔥 최고 하락폭(MDD) 단지 Top 3 (최저호가 기준):
"""

    for i, t in enumerate(top_drop):
        prompt += f"  {i+1}. {t['name']} {t['pyeong']} (최고가 대비 {t['mdd_rate']:.2f}% 하락, 현재 최저호가 {t['lowest_ask']}원)\n"
        
    prompt += "\n- 🏃‍♂️ 최근 30일간 거래량이 가장 많았던 단지 Top 3:\n"
    for i, t in enumerate(top_vol):
        prompt += f"  {i+1}. {t['name']} {t['pyeong']} (최근 30일 {t['month_vol']}건 성사)\n"
        
    prompt += "\n이 데이터를 바탕으로 멋진 마크다운 형식의 일일 시황 리포트를 작성해줘."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    if res.status_code == 200:
        try:
            generated_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            report_dir = os.path.join("web", "src", "data", "reports")
            os.makedirs(report_dir, exist_ok=True)
            today_str = datetime.now().strftime("%Y-%m-%d")
            out_path = os.path.join(report_dir, f"report_{today_str}.md")
            
            # Also save latest for easy frontend direct hit
            latest_path = os.path.join("web", "src", "data", "daily_market_report.md")
            with open(latest_path, "w", encoding="utf-8") as lf:
                lf.write(generated_text)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(generated_text)
            print("✅ 일일 마켓 리포트 작성 성공!")
        except Exception as e:
            print("API 응답 파싱 실패:", e)
    else:
        print("API 호출 실패:", res.text)

if __name__ == "__main__":
    generate_market_report()
