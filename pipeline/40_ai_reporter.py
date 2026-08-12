import os
import json
import logging
from datetime import datetime, timedelta, timezone
from google import genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import ssl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def fetch_article_content(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, context=ctx, timeout=5).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        # 기사 본문 추출 (주로 p 태그나 특정 클래스를 가진 div)
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        # 네이버 뉴스 등 리다이렉트 페이지일 경우 대비
        if len(text) < 100:
            divs = soup.find_all('div', style=False)
            text = " ".join([div.get_text().strip() for div in divs if len(div.get_text().strip()) > 50])
            
        return text[:800] # 토큰 절약을 위해 800자 제한
    except Exception as e:
        return f"내용 추출 실패 ({str(e)})"

def run():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY not found!")
        return
        
    client = genai.Client(api_key=api_key)
    
    KST = timezone(timedelta(hours=9))
    today_str = datetime.now(KST).strftime('%Y-%m-%d')
    output_dir_report = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'reports')
    output_dir_news = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data')
    os.makedirs(output_dir_report, exist_ok=True)
    
    # 1. 최신 뉴스 3건 스크래핑 및 본문 추출
    logging.info("Fetching news contents...")
    news_path = os.path.join(output_dir_news, 'latest_news.json')
    news_items = []
    if os.path.exists(news_path):
        with open(news_path, 'r', encoding='utf-8') as f:
            news_items = json.load(f)[:3] # 상위 3건만 피딩
            
    recent_news_context = ""
    for idx, item in enumerate(news_items):
        content = fetch_article_content(item['link'])
        item['body_summary'] = content
        recent_news_context += f"[기사 {idx+1}] 제목: {item['title']}\n언론사: {item.get('source', '알수없음')}\n본문 일부: {content}\n\n"
        
    # 2. KB50 통계 요약 (토큰 크기 문제로 핵심 데이터만 추출)
    logging.info("Summarizing KB50 stats...")
    kb50_path = os.path.join(output_dir_news, 'kb50_stats.json')
    with open(kb50_path, 'r', encoding='utf-8') as f:
        kb50 = json.load(f)
        
    rep_stats = []
    for c in kb50:
        cx_name = c['complex']['name']
        if not c['stats']: continue
        # 대표평형(국평 84㎡ 위주, 최근 거래 활성도순) 추출: 프론트엔드 page.tsx와 동일하게 맞춤
        def score(s):
            is_alive = False
            rp = s.get('recent_deal_absolute')
            if rp and rp.get('date'):
                try:
                    d = datetime.strptime(rp['date'], '%Y-%m-%d')
                    if (datetime.now() - d).days <= 365:
                        is_alive = True
                except: pass
            
            mka = s.get('match_key_area', 0)
            group_dist = 0 if 82 <= mka <= 85 else abs(mka - 84)
            return (not is_alive, group_dist, -(s.get('max_month_volume', 0)), -s.get('highest_deal_price', 0))
            
        best_stat = sorted(c['stats'], key=score)[0]
        rp = best_stat.get('recent_deal_absolute', {}).get('price') if best_stat.get('recent_deal_absolute') else best_stat.get('highest_deal_price', 0)
        ath = best_stat.get('highest_deal_price', 0)
        ask = best_stat.get('current_lowest_ask', 0)
        
        real_drop = ((rp - ath) / ath) * 100 if ath > 0 and rp else 0
        ask_drop = ((ask - ath) / ath) * 100 if ath > 0 and ask else 0
        # 갭 = 최저호가 변동률 - 실거래가 변동률
        # (예: 호가는 -5% 방어 중인데 실거래는 -20% 찍혔다면, 갭은 +15%p -> 호가가 높게 매달려있는 눈치보기)
        # (예: 호가는 -25%로 던지는데 실거래는 -10%라면, 갭은 -15%p -> 호가가 빠르게 붕괴되는 패닉셀)
        gap = ask_drop - real_drop
        
        rep_stats.append({
            'name': cx_name,
            'pyeong': best_stat['pyeong_name'],
            'ath': ath,
            'recent': rp,
            'ask': ask,
            'real_drop': round(real_drop, 2),
            'ask_drop': round(ask_drop, 2),
            'gap': round(gap, 2)
        })
        
    avg_real_drop = round(sum(s['real_drop'] for s in rep_stats) / len(rep_stats), 2)
    avg_ask_drop = round(sum(s['ask_drop'] for s in rep_stats) / len(rep_stats), 2)
    
    # 눈치보기 심함 (호가가 실거래보다 비정상적으로 높은 단지)
    gap_sorted = sorted(rep_stats, key=lambda x: x['gap'], reverse=True)[:5]
    # 호가 항복/패닉셀 (호가가 실거래보다 비정상적으로 붕괴된 단지)
    ask_drop_sorted = sorted(rep_stats, key=lambda x: x['gap'])[:5]
    
    data_context = f"""
    [RealFifty 오늘자 마켓 데이터 요약 ({today_str})]
    - 전체 50개 대장주 평균 실거래가 하락률: {avg_real_drop}%
    - 전체 50개 대장주 평균 최저호가 하락률: {avg_ask_drop}%
    
    [눈치보기 심한 단지 Top 5 (실거래 폭락에도 호가는 안 내리는 단지들)]
    {json.dumps(gap_sorted, ensure_ascii=False)}
    
    [급매 출회/호가 항복 단지 Top 5 (호가가 더 깊게 하락한 단지들)]
    {json.dumps(ask_drop_sorted, ensure_ascii=False)}
    """
    
    # 3. Gemini 보고서 생성
    logging.info("Generating Daily Report via Gemini...")
    report_prompt = f"""
    너는 'RealFifty 수석 분석관 김리얼'이야. 시세 데이터와 최신 뉴스를 엮어서 인사이트 넘치고 활기찬 문체로 마크다운 리포트를 작성해.
    
    데이터 요약:
    {data_context}
    
    오늘의 관련 뉴스:
    {recent_news_context}
    
    요구사항:
    1. 오늘 시장 상황을 요약하는 매력적인 마크다운 제목(# 📊 RealFifty 일일 마켓 브리핑)으로 시작할 것.
    2. 전체 50개 대장주의 하락률 수치를 바탕으로 묵직한 장세 진단을 먼저 던질 것.
    3. 눈치보기 단지와 호가하락(항복) 단지 데이터를 구체적인 아파트 이름과 수치로 표/리스트로 보여줄 것.
    4. [매우 중요] 함께 전달된 [오늘의 관련 뉴스]들은 언론사들의 과장이나 선동(예: 신고가 랠리, 반등 등)일 확률이 매우 높음. 뉴스의 주장을 무조건 믿고 원인으로 쓰지 마! 만약 기사는 '상승/신고가'를 외치는데 우리의 데이터가 '폭락/하락'을 가리킨다면, "언론은 상승이라고 호들갑 떨지만 실제 RealFifty 대장주 데이터는 -8%대 하락으로 정반대의 진실을 말해주고 있다"며 언론 기사를 매섭게 비판하고 반박하는 스탠스로 작성할 것. 데이터가 곧 진리임을 강조.
    5. 친근하면서도 팩트(데이터)를 무기로 언론을 꼬집는 단호한 전문가 톤앤매너 유지.
    """
    
    res_report = client.models.generate_content(model='gemini-3.5-flash', contents=report_prompt)
    report_md = res_report.text
    
    with open(os.path.join(output_dir_report, f'report_{today_str}.md'), 'w', encoding='utf-8') as f:
        f.write(report_md)
        
    logging.info("🎉 40_ai_reporter.py Completed successfully!")

if __name__ == '__main__':
    run()
