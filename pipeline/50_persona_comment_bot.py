import os
import json
import random
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 환경변수 로드
load_dotenv(".env")
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

if not all([supabase_url, supabase_key, gemini_api_key]):
    logging.error("필수 환경변수가 누락되었습니다. (.env 파일을 확인해주세요)")
    exit(1)

# 클라이언트 초기화
supabase: Client = create_client(supabase_url, supabase_key)
ai_client = genai.Client(api_key=gemini_api_key)

# 1. 페르소나 정의
PERSONAS = {
    "extreme_bull": {
        "name": "강성 폭등이 (Extreme Bull)",
        "vote": "bull",
        "description": "화폐가치 하락, 인플레이션, 서울 공급 부족을 맹신합니다. 하락장을 잠시 지나가는 소나기로 취급합니다. 말투는 단호하고 상승을 확신합니다. (예: 줍줍 못하면 평생 벼락거지 됩니다.)"
    },
    "extreme_bear": {
        "name": "강성 폭락이 (Extreme Bear)",
        "vote": "bear",
        "description": "고금리 지속, PF 부실, 인구 절벽 등을 근거로 대세 하락을 주장합니다. 상승론자들을 비꼬는 말투를 사용합니다. (예: 이 가격에 설거지 당하는 흑우 없재? 전고점 회복은 꿈도 꾸지 마시길.)"
    },
    "quant": {
        "name": "냉철한 데이터 분석가 (Quants)",
        "vote": "neutral", # 때에 따라 bull/bear가 될 수 있지만 기본은 중립/관망 스탠스로 설정
        "description": "감정을 배제하고 오로지 MDD(전고점 대비 하락률), 거래량, 전세가율 데이터를 바탕으로 이야기합니다. 객관적이고 전문가스러운 말투를 사용합니다."
    },
    "real_demand": {
        "name": "불안한 무주택 실수요자 (Real Demand)",
        "vote": "neutral",
        "description": "사고 싶지만 물릴까봐 무서워서 질문을 많이 던집니다. 약간 불안해하며 조언을 구하는 3040 세대의 말투입니다. (예: 지금 하락장인가요 상승장 초입인가요? 너무 고민됩니다 ㅠㅠ)"
    },
    "gap_investor": {
        "name": "단기 갭투자자 (Gap Investor)",
        "vote": "bull",
        "description": "거시 경제보다는 '전세 갭'과 '단기 호재'에만 관심이 많습니다. 실행력이 빠르고 실전 투자자 느낌이 나는 말투입니다. (예: 전세 빼기 쉬워서 투자금 2억이면 돌려봅니다.)"
    }
}

def generate_comment_data(complex_name: str, persona_key: str) -> dict:
    persona = PERSONAS[persona_key]
    
    prompt = f"""
당신은 대한민국 부동산 커뮤니티의 유저입니다. 
다음 페르소나에 완벽하게 빙의하여 '{complex_name}' 아파트에 대한 커뮤니티 댓글과 어울리는 닉네임을 작성해주세요.

[당신의 페르소나]
- 유형: {persona['name']}
- 성향: {persona['description']}

[작성 규칙]
1. 댓글 길이는 50자 ~ 150자 내외의 짧은 인터넷 커뮤니티 댓글 스타일로 작성하세요. (존댓말, 반말 섞어서 자연스럽게)
2. AI나 봇이라는 느낌이 전혀 들지 않도록 감정과 뉘앙스를 담아주세요.
3. 닉네임은 페르소나 성향에 맞는 3자~8자 길이의 한국어 닉네임을 창작하세요. (예: 강남가즈아, 영끌30대, 데이터맹신)
4. '{complex_name}'의 이름을 자연스럽게 언급하거나 유추할 수 있게 작성하세요.
5. 오직 아래 JSON 형식으로만 출력하세요. 마크다운 기호(```json 등)는 절대 포함하지 마세요.
{{
  "nickname": "창작한닉네임",
  "comment": "댓글본문"
}}
"""
    
    response = ai_client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )
    
    try:
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        logging.error(f"JSON 파싱 에러: {e}")
        return {"nickname": "부동산관망러", "comment": response.text.strip()}

def run_bot():
    logging.info("페르소나 봇 활성화: 시작합니다.")
    
    # 1. 아파트 단지 목록 가져오기 (랜덤으로 3개 선택)
    res = supabase.table("complexes").select("id, name").execute()
    complexes = res.data
    
    if not complexes:
        logging.error("아파트 단지 정보가 없습니다.")
        return
        
    target_complexes = random.sample(complexes, min(3, len(complexes)))
    
    # 2. 각 아파트에 대해 댓글 생성 및 삽입
    for comp in target_complexes:
        complex_id = comp['id']
        complex_name = comp['name']
        
        # 랜덤으로 1~2명의 페르소나 선택
        num_comments = random.randint(1, 2)
        selected_personas = random.sample(list(PERSONAS.keys()), num_comments)
        
        logging.info(f"[{complex_name}] 단지에 {num_comments}개의 봇 댓글을 생성합니다...")
        
        for p_key in selected_personas:
            persona_info = PERSONAS[p_key]
            try:
                # Gemini 엔진으로 JSON 데이터 생성 (닉네임 + 댓글)
                bot_data = generate_comment_data(complex_name, p_key)
                comment_text = bot_data.get("comment", "")
                author_name = bot_data.get("nickname", "폭락폭등관망")
                
                logging.info(f" -> [{persona_info['name']}] 닉네임: {author_name}, 댓글: {comment_text}")
                
                # DB Insert
                insert_data = {
                    "complex_id": complex_id,
                    "is_bot": True,
                    "author_name": author_name,
                    "persona_type": p_key,
                    "vote": persona_info['vote'],
                    "content": comment_text,
                    # created_at은 DB 기본값(NOW()) 사용
                }
                
                supabase.table("community_comments").insert(insert_data).execute()
                logging.info(f" -> 성공적으로 DB에 저장되었습니다.")
                
            except Exception as e:
                logging.error(f"댓글 생성/저장 중 오류 발생 ({complex_name} - {p_key}): {e}")

    logging.info("봇 동작이 완료되었습니다.")

if __name__ == "__main__":
    run_bot()
