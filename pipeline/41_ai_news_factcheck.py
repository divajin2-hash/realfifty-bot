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
        gap = abs(real_drop - ask_drop)
        
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
    
    # 갭 큰 단지 (눈치보기 심함)
    gap_sorted = sorted(rep_stats, key=lambda x: x['gap'], reverse=True)[:5]
    # 호가 하락 깊은 단지 (항복/급매)
    ask_drop_sorted = sorted(rep_stats, key=lambda x: x['ask_drop'])[:5]
    
    data_context = f"""
    [RealFifty 오늘자 마켓 데이터 요약 ({today_str})]
    - 전체 50개 대장주 평균 실거래가 하락률: {avg_real_drop}%
    - 전체 50개 대장주 평균 최저호가 하락률: {avg_ask_drop}%
    
    [눈치보기 심한 단지 Top 5 (실거래 폭락에도 호가는 안 내리는 단지들)]
    {json.dumps(gap_sorted, ensure_ascii=False)}
    
    [급매 출회/호가 항복 단지 Top 5 (호가가 더 깊게 하락한 단지들)]
    {json.dumps(ask_drop_sorted, ensure_ascii=False)}
    """
    
    # No Daily Report Generation in this script. Only FactCheck!
        
    # 4. Gemini 팩트체크 JSON 생성
    logging.info("Generating FactCheck API JSON via Gemini...")
    factcheck_prompt = f"""
    너는 가짜뉴스/과장보도를 판별하는 'RealFifty 팩트체커'야.
    제공된 [오늘의 뉴스]들을 모두 읽고, 내용이 매우 유사하거나 복붙(어뷰징)된 기사들이 있다면 병합하여 가장 대표적인 기사 1~2개만 엄선해.
    그리고 그 엄선된 1~2개의 최고 핵심 기사에 대해서만 [RealFifty 데이터]를 철저한 근거로 삼아 과장인지 사실인지 팩트체크해 줘.
    결과는 반드시 1개 이상 2개 이하의 원소를 가진 완벽한 JSON 배열 형태로만 출력해야 해. 마크다운 백틱 안됨(```json ... ``` 안됨). 시작과 끝이 [ 와 ] 이어야 함.
    
    데이터:
    {data_context}
    
    오늘의 뉴스:
    {recent_news_context}
    
    출력 형식(예시):
    [
      {{
        "title": "기사 실제 제목",
        "link": "기사 URL (제공된 news_items에서 가져올 것)",
        "source": "언론사",
        "pub_date": "원래 제공된 시간",
        "verdict_type": "과장 보도 주의" 또는 "팩트 일치",
        "body_summary": "기사 본문에서 주장하는 바를 1-2줄 핵심 요약",
        "factcheck_content": "RealFifty 분석결과: 데이터에 따르면 평균 하락률이 어쩌고... 하면서 반박하거나 동의하는 5~6줄 깊이있는 분석 텍스트"
      }}
    ]
    * 절대 제공받은 뉴스와 똑같은 개수를 만들지 말고, 중복을 확실히 제거하여 1~2개의 핵심 기사 팩트체크 오브젝트만 배출해 (배열 원소 개수 최대 2개).
    """
    
    # 원본 뉴스 객체들을 프롬프트가 링크를 가져갈 수 있도록 컨텍스트로 제공
    res_factcheck = client.models.generate_content(model='gemini-3.5-flash', contents=factcheck_prompt + f"\n[원본 JSON 구조]\n{json.dumps(news_items, ensure_ascii=False)}")
    
    raw_json = res_factcheck.text.strip()
    if raw_json.startswith('```json'): raw_json = raw_json[7:]
    if raw_json.startswith('```'): raw_json = raw_json[3:]
    if raw_json.endswith('```'): raw_json = raw_json[:-3]
    
    try:
        factcheck_data = json.loads(raw_json.strip())
        with open(os.path.join(output_dir_news, 'factcheck_news.json'), 'w', encoding='utf-8') as f:
            json.dump(factcheck_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Failed to parse FactCheck JSON: {e}\nRaw output: {res_factcheck.text}")

    logging.info("🎉 40_ai_reporter.py Completed successfully!")

if __name__ == '__main__':
    run()
