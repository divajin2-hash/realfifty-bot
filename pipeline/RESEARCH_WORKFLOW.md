# RealFifty 리서치 / 팩트체크 v2

## 리포트
기존 32_master_daily_run.py → 40_ai_reporter.py 진입점을 유지합니다.
40_market_report_agent.py도 동일한 research_core.run_report를 호출해 생성 규칙을 통일합니다.

```powershell
python pipeline/40_ai_reporter.py --preview  # 계산 결과만, API 호출 없음
python pipeline/40_ai_reporter.py            # Gemini 생성 → JSON 검증 → 날짜별 JSON/Markdown 저장
```

pipeline/.env의 GEMINI_API_KEY를 사용합니다. GEMINI_MODEL 기본값은 gemini-3.6-flash입니다.
환경변수로 다른 유효 모델을 지정할 수 있습니다. 키는 로그·결과·URL에 남기지 않습니다.
프롬프트: prompts/daily_report.md. 숫자는 Python에서 계산, AI 문단에는 근거 ID를 연결합니다.
숫자 리터럴·미등록 근거 ID·누락 섹션이 있으면 기존 보고서를 덮어쓰지 않습니다.
보고서는 생성 시점의 스냅샷을 함께 보관하므로 과거 AI 본문과 오늘 숫자가 섞이지 않습니다.
이전 Markdown만 있는 날짜는 레거시 원문으로 명시하고 현재 브리핑과 구분합니다.

## 팩트체크
1. /news에서 제목 기반 후보 유형을 확인하고 원문을 읽습니다.
2. 검증할 주장·시군구·법정동·대상/비교 기간을 입력하고 범위 일치를 확인합니다.
3. 요청은 web/src/data/factcheck/queue에 저장됩니다. 브라우저 요청은 유료 API를 직접 실행하지 않습니다.
4. 기존 아침 실행의 41_ai_news_factcheck.py가 확정된 요청을 최대 3건 처리합니다. 미확정 기사를 자동으로 참/거짓 판정하지 않습니다.

```powershell
python pipeline/41_ai_news_factcheck.py --process-queue --limit 3
python pipeline/41_ai_news_factcheck.py --process-queue --ai  # 선택: 계산 이후 AI 설명 생성
python pipeline/41_ai_news_factcheck.py --process-queue --retry --limit 1
```

RTMS_API_KEY로 MOLIT 아파트 매매 상세 API를 호출합니다. 시군구/계약월별 모든 페이지를 조회하고 totalCount를 대조합니다.
results에 결과, raw에 수집 원자료를 저장합니다. 원장 다운로드에는 원자료와 SHA-256도 포함됩니다.
원자료 해시는 ensure_ascii=False, sort_keys=True로 직렬화한 UTF-8 JSON 기준입니다.
오류 응답을 0건으로 취급하지 않습니다. 실패 재시도 시 이전 성공 결과를 보존합니다.

### 방법과 판정 한계
- 거래량: 해제 제외, 직거래 포함. 동일 일수 또는 동일 수의 완료 월끼리 비교합니다.
- 가격: 중개거래, 같은 단지·정확 면적·5개 층 구간. 비교 기간 2건 이상 중위가격 대비 ±1%를 보합으로 둡니다.
- 가격 비교 20건 미만 또는 비교율 60% 미만은 판단 유보. 60% 이상 방향만 우세 표시합니다.
- 가격 분포 결과를 가격지수 기사의 일치 판정에 사용하지 않습니다.
- 최근 종료 기간은 31일 관측 여유 전까지 잠정/판단 유보. 이는 품질 규칙이며 법적 신고기한을 정의하지 않습니다.
- 전국/지방/서울 전체 주장에는 해당 전체 지역 통계가 필요합니다. 현재 요청은 한 시군구 단위입니다.
- 법정동 이름은 API umdNm과 정확히 일치해야 합니다. 다른 표기는 0건/자료부족으로 남을 수 있습니다.
- 고유 거래 ID가 없어 동일 날짜·가격의 원자료 행을 임의로 제거하지 않습니다.
- RealFifty는 동일 동의 현재 보조 표본만 제시합니다. 기사 대상 기간의 모집단 대체 자료가 아닙니다.
- 언론사 정확도, 기사 신뢰도 점수, 전망 확률은 생성하지 않습니다.

## 운영 범위
현 단계는 사용자 요청대로 로컬 검토용입니다. 여러 서버/동시 작업자의 파일 잠금이나 인증은 포함하지 않았습니다.
기존 factcheck_history.json은 보존되지만 새 판정 화면에서는 사용하지 않습니다.
실제 기사별 결과는 범위가 확정된 요청을 실행한 뒤 채워집니다.

## 검증
python pipeline/test_research.py
web에서 npm run test:complex
web에서 node node_modules/typescript/bin/tsc --noEmit --incremental false

공식 문서:
- https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash
- https://www.data.go.kr/data/15126468/openapi.do
