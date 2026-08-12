# KB50 댄쇱  諛 ㅼ  (2026-07-24 湲곗)

##  猷 寃
- GitHub Actions `daily_bot.yml`: 留ㅼ KST   ㅽ ㅼ 猷
- GitHub Repository Secrets 3媛 깅 猷: `SUPABASE_URL`, `SUPABASE_KEY`, `RTMS_API_KEY`
- `31_daily_rtms.py`: 援遺 ㅺ굅媛 理洹 2媛移 留ㅼ 吏
- `18_naver_batch.py`: ㅼ대 理 멸 吏 + MDD 怨  `pyeong_stats` 대 
- `19_build_json_db.py`: `pyeong_stats` ㅼ 멸瑜 `kb50_stats.json` 諛
- `32_master_daily_run.py`:  ㅽщ┰몃ㅼ 濡 ㅽ 留ㅽ ㅽщ┰

## 截 ⑥ 듭 臾몄: ㅼ대  留ㅽ

### 臾몄 ㅻ
- 援遺 ㅺ굅媛: **⑸㈃** 湲곗 (: 84.98  `match_key_area = 84`)
- ㅼ대 ptpNo: ⑥蹂  怨 ID. 媛 ptpNo留  ⑸㈃ 
-  `18_naver_batch.py` `match_key_area`(⑸㈃)濡 `spcMin/spcMax`(怨듦硫댁)  怨  洹쇱ъ 遺
- ** 諛⑸**: ptpNo ⑸㈃ 留ㅽ DB  踰 ν대怨 留ㅼ 李몄“

### 닿껐댁  : `20_seed_pyeong_map.py` 
```
紐⑺: 50媛 ⑥  泥  {ptpNo, ⑸㈃, 紐}  pyeong_map 대 
ㅽ:   踰留 濡而ъ ㅽ (댄 遊  대留 李몄“)
諛⑸: headless=False + ⑥蹂 2~3珥 대 Naver 李⑤ 
API: https://new.land.naver.com/api/complexes/{complex_no}
       complexPyeongDetailList[].{ptpNo, pyeongNm, exclusiveArea}
```

### Supabase  대 (吏 쇰㈃  )
```sql
CREATE TABLE pyeong_map (
  id SERIAL PRIMARY KEY,
  complex_id INTEGER REFERENCES complexes(id),
  ptp_no TEXT,
  pyeong_name TEXT,
  exclusive_area INTEGER,
  UNIQUE(complex_id, ptp_no)
);
```

### 20_seed_pyeong_map.py   18_naver_batch.py  諛⑺
1. `pyeong_map` 대 대 ⑥ {ptpNo, exclusive_area} 紐⑸ 遺ъㅺ린
2. exclusive_area濡 `rtms_transactions` ATH(理怨媛) 留ㅼ묶
3. ptpNo濡 ㅼ대 URL   理 멸 ㅽщ
4. MDD 怨  `pyeong_stats` 

##   18_naver_batch.py 諛⑹ 
- URL: `complexes/{complex_no}?a=APT&b=A1&spcMin={min}&spcMax={max}&prcSort=asc`
- 移대 ㅽ몄 `/84m짼` 쇰 ⑸㈃ 異異  짹2.0 ㅼ감  
- 臾몄: spc 洹쇱 怨곗 ⑥蹂 몄감濡 由  

##  GitHub Actions 遊 ㅽ 
```
31_daily_rtms.py      援遺 ㅺ굅媛 理洹 2媛 吏
18_naver_batch.py     ㅼ대 理 멸 + MDD 怨  pyeong_stats 
19_build_json_db.py   kb50_stats.json  (濡몄)
30_daily_snapshot.py  ㅻ 대 
```

## 寃 蹂 (pipeline/.env)
- `SUPABASE_URL`: Supabase 濡 URL
- `SUPABASE_KEY`: service_role  (곌린 沅)
- `RTMS_API_KEY`: 援遺 怨듦났곗댄 API 


##  [洹 ] ㅼ대 ㅺ굅媛 댁 湲곕 珥諛  留ㅽ 
**(2026-07-30 곗댄)**

###  대 媛
 ㅼ대 멸 (ptpNo)怨 援遺 ㅺ굅媛 ⑸㈃ 媛 留ㅽ " ⑥" "짹2 몄 蹂"  대━ㅽ 쇰━ 議댄怨 ,  ㅼ감 명곗 몄 ('59' vs '60' ) ⑸.
ъ⑹  곕Ⅴ硫, ㅼ대 遺 대 **[/ㅺ굅媛] ** 議고硫 ㅼ대 ㅼㅻ媛 媛  (ptpNo)怨 援遺 ㅺ굅媛 곗댄곕 1:1濡 寃고⑺ 蹂댁ъ＜怨 듬.
곕━媛  援李 곗댄곕 고硫 ㅼ감 0% 臾닿껐 留ㅽ 대 援ъ  듬.

### 截 援ы ④ (Action Items)

1. **ㅼ대 ㅺ굅媛 댁 ㅽщ  (異)**
   - 1 (Seed) ㅽщ┰ 援ъ.
   - ㅼ대 媛蹂 (ptpNo) ⑥濡 吏 , 몄 **怨쇨굅 ㅺ굅媛 댁 (嫄곕쇱, 嫄곕湲, 痢듭)** (1~2嫄) 吏.

2. **援遺 DB  議 (Cross-Validation)**
   - 蹂댄 ㅼ대諛 ㅺ굅媛 (吏/痢/媛寃) 湲곗〈 援ъ 援遺 DB(`rtms_transactions`) 湲곗쇰 `SELECT` 荑쇰━ 議곗.
   - 쇳寃 100% 議곌굔 쇱 援遺 肄瑜 蹂 援遺 痢≪ `⑸㈃(match_key_area)` 異異.

3. **臾닿껐 留ㅽ 대(`pyeong_map`) 援ъ**
   -  議곗 듯 `[援遺 湲곗 ⑸㈃]  [ㅼ대 痢 怨듦硫댁(pyeongNm) + ptpNo]`   李몄“ 대 .
   - 대 DB 濡嫄곕 JSON쇰 怨.

4. **댄쇱 寃고 諛 媛**
   - 쇱 댄쇱(`19_build_json_db.py`, `20_mdd_bridge.py`)   諛⑷ 깅  留ㅽ 대 理곗 湲곗쇰 곕Ⅴ濡 濡吏 蹂寃.
   -  ㅼ감瑜 蹂댁湲   ы대 '몄 硫댁 蹂(Merge)' 濡吏 嫄고 肄⑸ ⑥ 湲곗쇰 듯.

> **湲곕 ④낵:**  ㅽ泥媛 硫 臾대━ 蹂듭≫  遺 媛吏 ⑥쇰, 怨듦硫댁 湲 쎌대  댁쇰 媛쇱 濡몄 踰洹멸 泥 諛⑹⑸.


##  [Phase 2] SNS Growth 留耳  댄쇱 援ъ (Next Step)
**(2026-08-03 곗댄)**

###  대 媛
10 移 곗댄곕댁 湲곕 諛 留ㅽ 諛 留ㅼ 踰 댄쇱몄 깆 100% 寃利  吏 '媛  諛 깊' 댁. 
湲곗〈 깃났쇰 援ъ ' 釉 쇱  댄쇱(P12)' 명곕 諛쇰, 濡 SNS 留耳  AI 댁   怨듭μ쇰 蹂⑸.

### 截 援ы ④ (Action Items)
1. ** 쇱/由댁  (YouTube/Instagram)**
   - 留ㅼ DB瑜 ㅼ 'ㅻ  湲곗 媛 留 (MDD)  Top 3' 異異.
   - AI瑜 듯  蹂  , TTS 諛 由(Remotion/FFmpeg) 蹂   濡.
2. **留耳 釉由ы 댁 梨 댁 (Threads/Telegram)**
   - 곗쇰━  ъ щ━ (/) 硫몃┃ 곗 諛 釉由ы ъㅽ  諛.
   -    lantertainer.com  URL 쎌.
3. **寃 ㅻ몄  (ㅻ 湲 遊)**
   - 몄ㅽ洹몃, 몃 #몃ℓ留, #遺곗ы 댁洹 寃臾 媛吏.
   - ㅽ몄  대 寃臾 留λ(二쇱, 吏) 留 遺 몄ъ댄 듦(: '媛援 洹몃쇱 理洹 멸 -30% 吏 湲곕' )瑜 湲濡  諛 湲곗  洹밸.


### ?? 진행 예정 (Next Steps - 2026-08-04)
1. **사이드바 메뉴 및 라우팅 재배치**: 좌측 '거래량 추이 통계' 바로 아래에 [시황 리포트 게시판] 및 메뉴 아이콘 재배치.
2. **디자인 전면 재편 (Phase 3)**: Vercel 스타일의 다크 모드 및 컴포넌트 색상 하드코딩 일괄 교체.
3. **관심단지 최저호가 트래킹 고도화 고민**: 50개 대장 아파트 스케일에서 발생하는 수집 시간(Scale-up) 이슈 완화 및 캐싱 전략 구상.

4. **소수점 누락 데이터 (NULL) 긴급 패치**: 래미안원베일리, 올림픽훼밀리 등 국토부 이름 미스매치나 API 타임아웃으로 소수점(exclusive_area_exact)이 NULL 처리된 4.9만 개 데이터 패치. (단, 원베일리는 재건축 이전 데이터 무시)

5. **전수 검사 및 네이버-국토부 완벽 정합성(Mapping) 매니페스트 구축**: 원베일리처럼 재건축/단지명 불일치로 인해 실거래가가 누락되거나 병합되는 단지가 없는지 50개 단지 전체를 대상으로 무결성 전수 검사 진행. 네이버 (평형/타입/전용면적)와 국토부 (단지명/전용면적 소수점)를 1:1로 하드매핑하는 마스터 테이블(또는 JSON 설정) 로직을 파이프라인에 최우선적으로 이식할 것.

## 🚀 [Phase 3] SNS 타겟 마케팅 에이전트 & 다중 페르소나 커뮤니티 에이전트 구축 전략
**(2026-08-12 업데이트 - UI 개편 및 로그인 도입 완료 이후 본격 가동)**

### 🗂️ 0. 콘텐츠 아카이빙 UI 고도화 (월간/연간 트리 구조)
수백 개의 데일리 리포트와 팩트체크가 누적될 경우를 대비한 아카이브 시스템 구축.
* **표출 방식:** 최신 5~7개만 리스트에 노출하고, 과거 데이터는 2026년 7월 (31건)과 같은 아코디언(트리) 뷰로 그룹화하여 렌더링 속도 최적화.
* **기대 효과:** UI 복잡도 하락 및 특정 과거 시점의 폭락/반등 기사를 쉽게 탐색 가능.

### 🎯 1. SNS 타겟 마케팅 에이전트 (트래픽 깔때기 구축)
최고의 팩트체크 시스템을 만들었으니, 이제 트래픽을 끌어올 **'행동 대장'**이 필요.

*   **팩트 폭격 콘텐츠의 재가공 (멀티 모달):**
    아침 9시에 생성된 [부동산 팩트체크] 데이터를 바탕으로, AI(42_sns_agent.py)가 SNS 플랫폼별 성격에 맞춰 알아서 폼 변환.
    *   **X (트위터) / 스레드:** 아드레날린을 자극하는 짧고 매운맛 스레드.
    *   **네이버 블로그:** 검색 노출(SEO)에 최적화된 정보성 긴 글 형식으로 가공하여 자동 포스팅.
*   **키워드 타겟팅 자동 답글 (인바운드 낚시):**
    X(트위터) API를 활용해 실시간으로 강남 아파트, 집값 등의 키워드 검색. 일반 유저 트윗을 발견하면 에이전트가 그 트윗의 맥락을 읽고 자연스럽게 개입. (예: 아시아선수촌 실거래-호가 갭 관련 데이터 인용 자동 답글)

### 💬 2. 다중 페르소나 커뮤니티 에이전트 (바람잡이 시스템 / 토론 생성기)
새로운 회원가입 페이지를 열었을 때 게시판이나 댓글 창이 텅 비어있으면 콜드스타트 발생. 이를 방지하기 위해 **AI 바람잡이(Seeding)** 투입.

*   **극단적 페르소나 설계:**
    최소 4가지 이상의 입체적인 AI 페르소나 DB 생성.
    1.  🔥 **영끌 낙관론자 (Bull_User):** 상승론, 방어력 강조
    2.  🧊 **폭락 비관론자 (Bear_User):** 비관론, 거품 붕괴 강조
    3.  🤓 **데이터 충 (Nerd_User):** 통계/마켓 데이터 중심 
    4.  👶 **초보 눈팅족 (Newbie):** 순수 질문, 감탄
*   **랜덤 시간대 자동 토론 생성 (43_comment_agent.py) :**
    새로운 팩트체크나 마켓 리포트가 업로드되면, 서버가 1~3명의 페르소나를 무작위 차출하여 제미나이에게 컨텍스트 제공. 생성된 댓들은 실제 회원처럼 Supabase comments 테이블에 시간차를 두고 삽입.
*   **심리적 트리거 (진짜 유저 유입 유도):**
    실제 유저가 사이트에 들어왔을 때, 상승 극단론자와 하락 극단론자(실제론 모두 AI)가 토론하는 것을 보고 반박, 동의를 위해 실제 회원가입과 댓글을 유도함.
