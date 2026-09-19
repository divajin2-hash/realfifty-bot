# RealFifty 인수인계 — 2026-09-18 (KST)

## 0. 다음 세션은 여기부터

- **목표:** 대한민국 대표 50개 아파트의 실거래·호가·매물 데이터를 해석하는 서비스. 현재 최우선은 **제공 정보의 정확성**이다. 매칭 보정/해제/정정을 시장 상승·하락이나 신규 계약으로 오인하게 만들지 않는다.
- 실제 프로젝트: `D:\appmaking\kb50_mdd` (과거 대화의 `kb50\_mdd` 표기는 실제 경로와 다름).
- 운영: https://www.lantertainer.com/ / Git: https://github.com/divajin2-hash/realfifty-bot
- 현재 브랜치: `v2-terminal-development`. 배포 커밋 **a19a6349d8cc16be233674cd310cf9ced3b21256**.
- `origin/main`, `origin/v2-terminal-development` 모두 위 커밋과 일치함을 문서 작성 중 `git ls-remote`로 확인했다.
- Vercel Production 배포 완료 및 운영 데이터/리포트/6인 의견 확인 완료. 배포: https://vercel.com/real50/realfifty/7fDx8toxJh6paihQLVDRzt15NEo3
- 이 문서 작성 요청은 문서 저장/상태 확인이다. **HANDOFF.md 자체는 아직 커밋·push하지 않았다.** 다음 작업은 현재 Git 상태부터 다시 확인한다.
- `web/AGENTS.md` 필독: Next.js 작업 전 `web/node_modules/next/dist/docs/` 관련 가이드를 읽을 것.

## 1. 현재 구현 상태

### 웹

Next.js 16.2.11 App Router, React 19.2.4, TypeScript, Recharts. `web/`가 Vercel 앱 루트다.

- `/`: 오늘의 시장, 지표·월별 흐름, 타입별 호가 변화, 특징 해석, 오늘의 AI 시장톡.
- `/market`: 50개 단지 표본의 가격 위치·호가 괴리·거래 추이 및 해석.
- `/complex`: 단지/평형 선택, 최근가·최고가·호가·전세·매물 수, 차트·거래 원장·의견 작성.
- `/report`: 근거 ID를 가진 AI 리서치, 기준 자료/시나리오/한계, 아카이브, 인쇄/PDF, 개인 저장.
- `/ai-talk`: 한 단지·한 타입을 여섯 고정 페르소나가 해석한 기록.
- `/guide`, `/improvements`, 피드백 제보 및 `/admin/feedback`.
- 이메일 링크 + 카카오 로그인, `/account`: 관심 단지, 저장 리포트, 의견, 호가 변화 기준, 탈퇴.
- 호가 변화는 하루 한 번 수집 자료와 설정 당시 가격 비교. **이메일/푸시 가격 알림 아님.**
- 인쇄/PDF 버튼은 현재 `ReportActions.tsx`에서 `window.print()`를 직접 호출한다. **PDF 자체는 로그인 제한이 없다.** 개인 리포트 저장은 회원 기능.
- 전세 0건이면 매물 없음으로 표시하고 전세가·전세가율을 임의 계산하지 않는다.
- 로고 홈 링크, 모바일 메뉴/레이아웃, 숫자와 한글 단위 폰트, 그래프/인쇄용 차트 등을 보완했다. 최근 인수인계 점검은 시각적 전 페이지 재검사가 아니라 테스트/타입 검사다.
- 팩트체크/‘데이터로 읽는 시장’은 사용자 결정으로 주 메뉴에서 제외. 50개 표본만으로 전국/기사 범위를 검증하지 않는다. 관련 코드·관리 화면·DB는 보존돼 있고 완전 삭제나 모든 작업 중단 상태는 아니다.

### 중요한 파일

| 위치 | 역할 |
|---|---|
| `web/src/app/TerminalShell.tsx` 및 스타일 | 공통 레이아웃·메뉴·지표·방법론 |
| `web/src/app/page.tsx`, `MarketCharts.tsx`, `MarketInterpretation.tsx` | 홈·차트·자료 해석 |
| `web/src/app/market/`, `web/src/app/complex/` | 시장 및 타입별 단지 분석 |
| `web/src/lib/complex-model.ts`, `complex-data.ts`, `market-data.ts`, `market-reading.ts` | 타입 키·대표 타입·공통 데이터·거래 비교 |
| `web/src/lib/daily-changes.ts` | 웹 호가 변화 데이터 |
| `web/src/lib/report-data.ts`, `ai-talk.ts` | 리포트/토론 로딩·공개 자격 필터 |
| `web/src/app/report/PrintTrendChart.tsx`, `ReportActions.tsx` | 인쇄 차트·PDF/저장 |
| `web/src/app/MemberActions.tsx`, `account/`, `auth/callback/` | 회원 동작·인증 복귀 |
| `web/src/lib/member-server.ts`, `account-lifecycle.ts`, `feedback-store.ts` | 서버 인증·탈퇴·피드백 저장 |
| `web/supabase/migrations/` | 회원/팩트체크 검토/탈퇴/피드백 SQL |
| `web/vercel.json` | 탈퇴 재시도 cron: UTC 18:00 (KST 다음날 03:00) |
| `web/next.config.ts` | 공개 환경변수에 서버 키가 들어가면 빌드 차단 |

## 2. 데이터 흐름과 운영 진입점

**실행 전에 부작용을 이해할 것:** `run_daily_bot_local.bat`는 단순 테스트가 아니다. 수집, DB 쓰기, 유료 AI 호출, 텔레그램 발송, Git commit/push, Vercel 배포까지 수행한다.

현재 `32_master_daily_run.py` 순서:

1. `pipeline/11_api_scraper_v2.py`: 로컬 네이버 호가·매물 수·전세·중개사 등 수집.
2. `daily_type_matching.py --asks pipeline/raw_daily_asks_YYYY-MM-DD.json`:
   - `recheck_rtms.py` 국토부 일반 매매 + 분양권/입주권 원본 갱신.
   - 로컬 네이버 타입별 거래 목록 수집 및 `build_type_trade_evidence.py` 대조.
3. `20_mdd_bridge.py`: 검증 자료를 이용한 `pyeong_stats` DB upsert.
4. `19_build_json_db.py`: 검증 원본으로 `kb50_stats.json` 생성, `build_daily_changes.py` 호출.
5. `30_daily_snapshot.py`: `daily_history` DB 스냅샷 저장 (정수 면적 그룹 구조는 여전히 남아 있음).
6. `36_build_chart_data.py`: 차트 출력 (호가 이력 등 DB 읽기 포함).
7. `36_build_macro_index.py`, `build_verified_macro.py`, `45_news_crawler.py`.
8. `40_ai_reporter.py` → `research_core.py`, `50_persona_comment_bot.py`.
9. `35_telegram_notify.py` 발송.
10. 배치 파일이 승인된 데이터 경로만 stage/commit 후 `HEAD:main`, `HEAD:v2-terminal-development` push.

예약 배치는 staged 변경이 있으면 중단한다. **작업 중 Git index를 남겨두지 말 것.** 자동 push는 fast-forward이며 강제 push 아님. 수동 이번 배포는 `git push --atomic origin HEAD:main HEAD:v2-terminal-development` 사용.

### 산출물

- `pipeline/raw_daily_asks_YYYY-MM-DD.json`: 타입별 일일 원본. 날짜별 미추적 파일 많음. 삭제 금지.
- `pipeline/rtms_recheck/{법정동앞5자리}-{YYYYMM}.json`, `rights-...`: 국토부 지역·월 원본 캐시.
- `pipeline/rtms_recheck/verified_full.json`: 2014년~현재 검증 거래, 단지 목록, 관측 시각, 원본 대조 결과.
- `pipeline/rtms_recheck/naver_daily/`: 네이버 타입별 거래 대조 캐시.
- `pipeline/type_trade_evidence.json`: 타입별 원본 거래 연결 근거.
- `pipeline/rtms_recheck/matching_status.json`: 타입 검증 결과.
- `web/src/data/kb50_stats.json`: 50개 단지의 타입별 웹 자료. `matching_version=area-v3`, `official_observed_at` 포함.
- `web/src/data/daily_changes.json`: 웹/텔레그램이 함께 사용하는 타입별 호가 비교.
- `web/src/data/macro_tx_index.json`, `macro_index.json`, `web/public/chart_data/`.
- `web/src/data/reports/report_YYYY-MM-DD.{json,md}`, `web/src/data/ai-talk/YYYY-MM-DD.json`.

## 3. 정확성 결정과 구현 이유

### 국토부가 거래 존재의 근거

- `complex_matching.py`: 차수/단지 이름을 보존하는 별명 매칭. 괄호를 무조건 제거해 1차·2차 등을 합치지 않는다.
- `type_matching.py`: 소수점 면적(Decimal 2자리) 또는 **국토부에 존재하는 거래에 대한 네이버 대조 근거**로 연결.
- 동일 면적에 여러 타입이면 공유 거래가 있을 수 있다. 네이버 목록에만 있는 거래를 국토부 실거래로 새로 삽입하지 않는다.
- `19_build_json_db.py`: 검증 파일 필수. legacy DB 거래로 되돌아가는 fallback 제거. 현재 웹 거래 범위는 검증된 2014년 이후 원본이다.
- 해제 거래와 직거래 제외는 현재 서비스 정책이다. 직거래를 가짜 거래로 판단하는 의미가 아니며, 향후 제공 범위 변경 시 명시적인 분리 설계가 필요하다.

### 2026-09-18 사고 조사 및 수정

텔레그램 ‘82개 실거래 가격 변경 그룹’은 신규 계약 82건이 아니었다. 매칭 보정 전 DB 스냅샷과 보정 후 대표 가격을 비교한 결과였다.

- 아시아선수촌 34.51억(7/9)은 직거래. 제외 후 이전 중개거래 42.5억(6/19)이 대표가가 되어 상승처럼 보였다.
- 이전 가격 11개는 해당 단지 원본에 없고 같은 계약일·금액·층이 다른 단지에서 발견됨(타워팰리스2→1, 장미2→1, 목동 다른 단지 등).
- 대표 타입 자체 변경도 11개 그룹 있었으며 원인 분류와 중복 가능.
- 신규 원본 확인에서 신반포2차 79.42㎡, 2026-09-11, 1층, 40억에 9/16 해제 표시 발견. 기존 수집 원본에는 없었음. 재조회 후 웹/차트에서 제외.

### 알림·AI

- `official_changes.py`: UI 대표 타입이 아닌 원본 거래 정체성의 Counter 비교. 중복 거래 수 보존. added/removed는 **추가 관측/목록 제외**이며 신규 계약·가격 방향으로 단정하지 않음.
- 최초 기준/조회 범위/단지 목록/매칭 규칙 해시 변경 시 `baseline` 또는 `scope_changed`로 집계 보류.
- `35_telegram_notify.py`는 `daily_history.recent_price`의 단순 전일 차이를 더 이상 실거래 상승/하락으로 발송하지 않음.
- 웹·텔레그램 호가 비교는 동일 타입 키(단지 번호+ptp), 같은 면적, 양쪽 양수 호가를 사용. 0→양수/양수→0는 등장·소멸로 분리.
- AI 생성 전 전체 표시 거래가 검증 원본에 있는지 검사. 원본 36시간 초과 또는 자료의 `official_observed_at` 불일치면 차단.
- 리포트/토론 공개에는 `accuracy_version=official-v1` 필요. 이전 문서는 파일 보존하되 공개 목록에서 제외. 현재 검증된 첫 공개 아카이브는 9/18 자료다.
- 오늘 리포트/6인 의견 재생성 및 운영 반영 완료. source_fingerprint와 생성 잠금으로 같은 입력 중복 호출 방지.
- 페르소나는 장기 낙관론자/하방 경계론자/데이터 분석가/실거주 매수자/전세 거주자/임대 투자자. 성향은 다르지만 상승·하락·관망 비율을 강제하지 않는다.

## 4. 재조회 정책 (배포 코드 반영 완료)

`rtms_refresh_policy.py`, `recheck_rtms.py`, `daily_type_matching.py`:

- KST 매일: 당월+이전 2개월 + 현재 각 타입의 최근 거래/최고가가 속한 월.
- 일요일: 당월 포함 최근 12개월 + 주요 거래 월.
- 첫 일요일(day<=7): 2014년부터 전체 기간. `--full-refresh` 수동 전체 갱신 가능.
- 지역·월 중복 제거, 일반 매매/분양권 원본 모두 조회. 캐시가 없는 범위는 추가 조회.
- 기존 `RTMS_REFRESH_FROM` 환경변수는 수동 호환용으로 남아 있어 설정되면 조회 범위를 넓힐 수 있다.
- 9/18 자료 dry-run: 217 지역·월 쌍, 두 원본 합계 434 작업(페이지 수/재시도 제외).
- 조회 실패가 하나라도 있으면 새 `verified_full.json` 발행 중단. master의 check/returncode를 통해 후속 단계 중단.
- 다음 일요일 9/20 최근 1년, 다음 첫 일요일 10/4 전체 범위 예정(해당 날 로컬 실행이 실제 이루어져야 함).

## 5. 외부 서비스·환경변수 — 값은 절대 문서에 쓰지 말 것

### 로컬

- Python `F:\anacon\python.exe`, Node `F:\node.exe`. PowerShell에서 `$env:PYTHONIOENCODING='utf-8'` 권장.
- 배치 파일은 `python`을 PATH에서 찾음. 다른 PC/계정으로 옮길 때 예약 작업의 PATH/Python 패키지 확인 필수.
- pipeline/.env: `SUPABASE_URL`, `SUPABASE_KEY`(서버 비밀 키), `RTMS_API_KEY`, `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- web/.env.local: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `CRON_SECRET`, `KAKAO_ADMIN_KEY`, `KAKAO_APP_ID`, 로컬 factcheck worker 관련 설정.
- 추가 코드 설정: `REALFIFTY_EMAIL_LOGIN_READY`(Vercel 이메일 로그인 표시 gate), `REALFIFTY_FEEDBACK_STORE`, `GEMINI_MODEL`, `PERSONA_MODEL`.
- 모델 기본값: report `gemini-3.6-flash`, persona `gemini-3.5-flash` (실제 산출물 model 필드/환경 override 확인). 유료 API 호출을 단순 테스트로 실행하지 말 것.

### Supabase / 인증

- 프로젝트 real50, ref `hqgggpddkpbewkryvfll`.
- 과거 공개 JS에 관리 키 노출 사고가 있었고 공개/서버 키 분리, 기존 legacy API 키 비활성화 및 JWT 관련 조치를 진행했음. **옛 키를 복원하지 말 것.** 실제 유효 상태는 대시보드에서 확인할 것.
- `NEXT_PUBLIC_*`에는 publishable/anon 키만. `sb_secret_*`, service_role, 카카오 Admin Key는 서버 전용. 키/토큰을 git·채팅·로그·문서에 출력하지 말 것.
- 이메일 SMTP: Resend, 발신 RealFifty <login@auth.lantertainer.com>. DNS 등록 완료 이력. 문의 주소는 임시 `jin2us80@daum.net`, 운영사 (주)랜터테이너.
- Kakao Developers 앱 ID 1579804. callback `https://hqgggpddkpbewkryvfll.supabase.co/auth/v1/callback`.
- 비즈 앱 이메일 권한 없는 상태에서 `account_email`, `profile_image` 요청해 KOE205가 발생했음. 현재 nickname 범위 기준. 임의로 scope 추가하지 말 것.
- 탈퇴: 서버 전용 카카오 연결 해제 + 삭제 대기열/RLS + cron 재시도. 인증/동일 출처/앱 검증을 제거하지 말 것. SQL 파일 존재만으로 외부 DB 적용을 새 세션에서 가정하지 말 것.
- Supabase 데이터 보관/지역 관련 지원 티켓 **SU-476073**. 사용자는 접수 메일만 공유했으며 최종 답변 수신은 이 세션에서 확인하지 못함.

### Vercel / GitHub

- project realfifty, team real50; projectId `prj_zzUInJZ5ZDFmWaa0M8uuWEPcUmDW`.
- 환경변수 변경은 재배포 필요. `.vercel/project.json`, `.env*`, 자격증명은 커밋하지 않는다.
- 마지막 확인 요금제 Hobby. 사용자와 Pro 전환 논의 있었으나 실제 유료 전환은 확인하지 못함. 상업 공개/마케팅 범위를 키우기 전에 최신 약관 적합성과 전환 여부 재확인; 자동 결제 금지.
- 네이버 요청은 GitHub 호스팅 러너에서 차단/timeout 경험. **로컬 수집 유지.** `.github/workflows/type_matching.yml` schedule 제거 + job false. daily_bot.yml.disabled 보존.
- `heal.yml`은 수동 DB repair workflow로 남아 있음. 원인 확인 없이 실행 금지.

## 6. 현재 예약 작업 / 안전한 종료

2026-09-18 인수인계 작성 중 Windows Task Scheduler 읽기 확인:

| 작업 | 상태 | 마지막 결과 | 다음 실행 |
|---|---|---|---|
| RealFifty_Daily_Bot | Ready | 9/18 00:05:05, 0 | 9/19 00:05:05 |
| RealFifty_Morning_Bot | Ready | 9/18 09:00, 0 | 9/19 09:00 |
| RealFifty_PersonaBot | Ready | 9/18 09:00, 0 | 9/18 13:00 |

- Daily는 run_daily_bot_local.bat. 현재 변경 후의 전체 예약 실행은 아직 관찰하지 않았다. 다음 회차 결과 확인 필요.
- Morning은 run_morning_bot_local.bat → 33_morning_news_run.py → 뉴스 수집/41_ai_news_factcheck.py 및 git add/commit/push. 주 메뉴에서 팩트체크를 뺐다고 이 작업이 중단된 것은 아님.
- Persona는 untracked run_persona_bot.bat → 50_persona_comment_bot.py. 일일 master와 중복 진입점이 있으나 fingerprint/lock은 존재. 정리 필요.
- 이번 문서 요청에서는 예약 설정을 바꾸거나 작업을 실행하지 않았다.
- 점검 시 실행 중 python/pythonw/git 프로세스 없음, AI `.generation.lock` 없음. Node 프로세스들은 사용자/Codex/개발 서버 등이 섞일 수 있어 종료하지 않았다.
- **Codex 세션은 종료 가능.** 단, PC를 끄거나 절전하면 로컬 예약 수집이 실행되지 않을 수 있다. Git 작업 폴더를 정리/삭제할 필요는 없다.

## 7. 해결되지 않은 문제·한계 (완료로 오인 금지)

1. **첫 새 정책 예약 실행 검증 미완료:** 단위 테스트/계획 dry-run은 통과했으나 새 범위로 전체 로컬 네이버+국토부 배치를 재실행하지 않음. 434 작업은 실제 API 응답 수가 아님.
2. **실행 누락 보완 없음:** 일요일/첫 일요일에 PC가 꺼져 있으면 다음 실행에서 주간/월간 범위를 자동 보충하지 않는다. 성공일 ledger 기반 catch-up 우선 검토.
3. **해제 후 대체 대표 거래:** 당일 refresh 월 선택은 이전 화면의 최근가/최고가 기준. 그 거래가 빠지면 새 대표가 된 과거 거래의 월이 당일 갱신 범위에 없을 수 있다. 재계산 후 새 참조 월 추가 검증(한정 반복) 필요성 검토.
4. **전 구간이 매일 새 원본은 아님:** verified_full.fetched_at은 조립 완료 시각. 과거 캐시별 조회 시각 노출/추적은 미흡. 36시간 gate가 모든 과거 행의 신선도를 보장하지 않는다.
5. **거래 변화는 관측 추가/제외까지만:** 정정·해제·신규 신고를 원본별 lifecycle로 완전히 분류하지 않음. added를 신규 계약으로 바꾸면 안 됨.
6. **비교 기준 보류:** to_month 변경(월 전환), complexes 순서/내용, source_rules 변경으로 scope_changed 가능. 초기 source_rules 도입으로 다음 회차 보류 가능. 정상적인 보수적 동작이지만 불필요한 reset 개선 여지 있음.
7. **원본 내 같은 계약일의 여러 거래:** 최근 거래는 일 단위로 정렬하므로 동률 시 ‘가장 마지막 실제 체결’이라고 단정 불가. 안정된 tie-break/범위 표시 개선 검토.
8. **기존 자동 작업 정리:** Morning/Persona 예약 작업 및 매일 뉴스 수집이 남음. 불필요한 API 비용/자동 commit 여부 확인 후 사용자 방향에 맞춰 비활성화·통합.
9. **원자적 전체 발행 아님:** verified_full과 개별 JSON은 atomic replace를 사용하지만 DB/여러 산출물 전체 트랜잭션은 아님. 중간 실패 시 로컬 파일/DB 일부가 바뀌어 있을 수 있음. 운영 push는 master 실패 시 중단.
10. **알림 순서:** 현재 Telegram 발송이 Git push/Vercel 성공보다 앞선다. 알림을 실제 배포 완료 후로 옮길지 검토.
11. **AI 내용:** 근거 ID/형식 검증은 있지만 자연어의 모든 수치·추론을 자동 증명하지 않는다. 한계·조건부 표현 유지. 과거 해설을 accuracy_version만 임의 덧붙여 노출하지 말 것.
12. **과거 보조 코드/문서:** ACCURACY_POLICY.md 하단의 ‘배포 미수행’은 작업 당시 기록으로 현재 상태와 다름. 이 HANDOFF의 배포 정보가 최신. 일부 master 주석은 인코딩 깨짐/옛 설명 존재.
13. **빌드 경고:** Next Turbopack NFT 추적 경고(`next.config.ts` → admin/factcheck route)는 남아 있으나 배포 빌드는 성공. 필요 시 파일 추적 범위 정리.
14. KB 선도아파트50 명단의 정확한 기준월은 과거 사용자 기억이 7~8월로 불확실했다. 공식 원본을 확인하지 않고 기준월을 단정하지 말 것.

## 8. Git 보존 사항 / 건드리지 말 것

현재 배포 코드 변경은 모두 a19a634에 반영됐다. 다만 작업 트리는 clean하지 않다.

추적 중이나 이번 배포와 무관하여 남긴 수정 4개:
- dump.html
- find_api.py
- web/src/data/factcheck/candidates.json
- web/src/data/latest_news.json

수집 원본, root 실험/디버그 Python·HTML·이미지, 미추적 run_persona_bot.bat, 스키마 CSV/SQL, 시안 zip 등 미추적 파일이 다수 있음. 파일 목록은 동반 `HANDOFF_git_status.txt` 또는 `git status --short` 확인.

- `git add .`, `git clean`, `reset --hard`, 원본 대량 삭제 금지. 명시적으로 파일을 선택하여 커밋.
- 사용자 기존 변경을 되돌리지 말 것. 캐시/근거/일별 원본 삭제는 다음 비교 및 재현을 깨뜨릴 수 있음.
- 비밀 키, 회원 자료, 로컬 .env와 인증 파일, 브라우저 인증 링크는 절대 커밋하지 말 것.
- 네이버 단독 거래를 국토부 원본에 추가하거나, 정수 면적 최근가 비교를 신규 거래 알림으로 복원하지 말 것.
- 검증 실패 시 진행하는 fallback, 강제 push, RLS 우회 확대, 무분별한 키 교체 금지.

## 9. 검증 결과 / 재현 명령

인수인계 작성 중 새로 확인:
- Python 단위 테스트 28개 통과: type_matching 9, daily_type_matching 2, daily_changes 2, official_changes 8, rtms_refresh_policy 7.
- Node 선택 테스트 13개 통과: complex-model, market-reading, member-editor, account-lifecycle (각 파일 내 추가 assertion 포함).
- `tsc --noEmit` 통과.
- Node 테스트는 첫 sandbox 실행에서 spawn EPERM 발생, 동일 테스트를 승인된 권한으로 재실행하여 통과. 코드 실패로 혼동하지 말 것. 한 PowerShell 명령의 마지막 exit code만으로 앞선 테스트 성공을 판정하지 말 것.
- 직전 작업에서 로컬 Next production build 및 Vercel production build 성공. 코드 변경이 없어 이 문서 작성 중 전체 build 재실행하지 않음.
- 직전 운영 확인: /, /market, /report, /ai-talk, 단지 API 모두 HTTP 200; 신반포2차 stats가 로컬과 완전 일치; report 제목·요약과 6인 judgment 전부 일치.
- 운영 자료 기준: `2026-09-18T03:00:56.775395+00:00` (KST 12:00:56), 원본 조립 `2026-09-18T03:00:10.164436+00:00`.

```powershell
Set-Location D:\appmaking\kb50_mdd
$env:PYTHONIOENCODING='utf-8'
& F:\anacon\python.exe -m unittest discover -s pipeline -p test_type_matching.py
& F:\anacon\python.exe -m unittest discover -s pipeline -p test_daily_type_matching.py
& F:\anacon\python.exe -m unittest discover -s pipeline -p test_daily_changes.py
& F:\anacon\python.exe -m unittest discover -s pipeline -p test_official_changes.py
& F:\anacon\python.exe -m unittest discover -s pipeline -p test_rtms_refresh_policy.py
Set-Location web
& F:\node.exe --test tests/complex-model.test.mjs tests/market-reading.test.mjs tests/member-editor.test.mjs tests/account-lifecycle.test.mjs
& F:\node.exe node_modules/typescript/bin/tsc --noEmit
# 필요 시: & F:\node.exe node_modules/next/dist/bin/next build
```

`pipeline/test*.py` 전체를 무작정 실행하지 말 것. 오래된 실험 파일 중 실제 API/DB를 호출하는 것이 있을 수 있다.

## 10. 다음 작업 순서

1. HANDOFF와 ACCURACY_POLICY, 해당 폴더 AGENTS를 읽고 git status/원격 커밋을 재확인.
2. 다음 Daily_Bot 첫 실행 로그·종료 코드·원본 refresh_policy·matching_status·AI 시각·실제 배포 커밋을 확인. 실패 시 기준 자료를 지우지 말고 해당 단계부터 원인 파악.
3. Morning/Persona 별도 예약 작업의 필요성, 자동 commit 대상과 실제 비용을 확인하고 중복 진입점 정리안을 제시/실행 범위 확인.
4. 재조회 성공 ledger와 누락된 주간/월간 catch-up, 새 대표 거래 월 재검증, 캐시별 조회 시각을 보강.
5. 원본 거래 lifecycle(해제/정정/추가 관측) 이력을 보존하고 동일 날짜 여러 거래 표시 방식을 정의. 검증되지 않은 상승·하락 숫자 공개 금지.
6. AI 원문 수치/근거 대조 테스트, Telegram 발송 시점/실패 복구 정리.
7. 이후 실제 사용자 피드백 기반 모바일·설명·리포트 개선. 전국 데이터 확장 전 기사 팩트체크를 다시 전면에 내세우지 않기.

## 11. 조사 자료 위치

- 작업 산출물: `E:\codex\2026-09-15\x20\outputs\RealFifty\`
  - `2026-09-18_실거래82그룹_국토부대조.csv`
  - `2026-09-18_정정알림_미발송.txt` (실제 발송 안 함)
  - `정보정확성_운영기준.md`
- 원본 조사/스크립트: `E:\codex\2026-09-15\x20\work\official-audit\`, `history-audit.json`, `audit_official.py`, `compare_official.py` 등.
- HANDOFF의 읽기용 사본과 Git 상태 목록도 outputs/RealFifty에 저장한다. 실제 후속 작업의 기준 파일은 프로젝트 루트 HANDOFF.md다.
