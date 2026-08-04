# KB50 파이프라인 현황 및 다음 작업 (2026-07-24 기준)

## ✅ 완료된 것들
- GitHub Actions `daily_bot.yml`: 매일 KST 자정 자동 실행 설정 완료
- GitHub Repository Secrets 3개 등록 완료: `SUPABASE_URL`, `SUPABASE_KEY`, `RTMS_API_KEY`
- `31_daily_rtms.py`: 국토부 실거래가 최근 2개월치 매일 수집
- `18_naver_batch.py`: 네이버 최저 호가 수집 + MDD 계산 → `pyeong_stats` 테이블 저장
- `19_build_json_db.py`: `pyeong_stats`의 실제 호가를 `kb50_stats.json`에 반영
- `32_master_daily_run.py`: 위 스크립트들을 순서대로 실행하는 마스터 스크립트

## ⚠️ 남은 핵심 문제: 네이버 평형 매핑

### 문제 설명
- 국토부 실거래가: **전용면적** 기준 (예: 84.98㎡ → `match_key_area = 84`)
- 네이버 ptpNo: 단지별 평형 고유 ID. 각 ptpNo마다 대응하는 전용면적이 있음
- 현재 `18_naver_batch.py`는 `match_key_area`(전용면적)로 `spcMin/spcMax`(공급면적) 필터 계산 → 근사치라 불정확
- **정확한 방법**: ptpNo와 전용면적 매핑을 DB에 한 번 저장해두고 매일 참조

### 해결해야 할 작업: `20_seed_pyeong_map.py` 작성
```
목표: 50개 단지 × 전체 평형의 {ptpNo, 전용면적, 평형명} 을 pyeong_map 테이블에 저장
실행: 딱 한 번만 로컬에서 실행 (이후 봇은 이 테이블만 참조)
방법: headless=False + 단지별 2~3초 딜레이로 Naver 차단 회피
API: https://new.land.naver.com/api/complexes/{complex_no}
      → complexPyeongDetailList[].{ptpNo, pyeongNm, exclusiveArea}
```

### Supabase에 필요한 테이블 (아직 없으면 생성 필요)
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

### 20_seed_pyeong_map.py 완성 후 18_naver_batch.py 수정 방향
1. `pyeong_map` 테이블에서 해당 단지의 {ptpNo, exclusive_area} 목록 불러오기
2. exclusive_area로 `rtms_transactions`의 ATH(최고가) 매칭
3. ptpNo로 네이버 URL 생성 → 최저 호가 스크랩
4. MDD 계산 → `pyeong_stats` 저장

## 🔧 현재 18_naver_batch.py 방식 요약
- URL: `complexes/{complex_no}?a=APT&b=A1&spcMin={min}&spcMax={max}&prcSort=asc`
- 카드 텍스트에서 `/84m²` 형식으로 전용면적 추출 후 ±2.0 오차 내 확인
- 문제: spc 근사 계산이 단지별 편차로 틀릴 수 있음

## 📋 GitHub Actions 봇 실행 순서
```
31_daily_rtms.py     → 국토부 실거래가 최근 2개월 수집
18_naver_batch.py    → 네이버 최저 호가 + MDD 계산 → pyeong_stats 저장
19_build_json_db.py  → kb50_stats.json 생성 (프론트엔드용)
30_daily_snapshot.py → 스냅샷 이력 저장
```

## 환경 변수 (pipeline/.env)
- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_KEY`: service_role 키 (쓰기 권한)
- `RTMS_API_KEY`: 국토부 공공데이터 API 키


## 🚀 [신규 제안] 네이버 실거래가 내역 기반 초정밀 평형 매핑 전략
**(2026-07-30 업데이트)**

### 💡 아이디어 개요
현재 네이버의 호가 평형(ptpNo)과 국토부의 실거래가 전용면적 간의 매핑은 "소수점 단수화"나 "±2㎡ 인접 병합" 등 휴리스틱 논리에 의존하고 있어, 소수점 오차나 펜트하우스 인식 누락('59' vs '60' 등)이 나타납니다.
사용자 제안에 따르면, 네이버 부동산 내부의 **[시세/실거래가] 탭**을 조회하면 네이버 스스로가 각 자사 평형(ptpNo)과 국토부의 실거래가 데이터를 1:1로 결합하여 보여주고 있습니다.
우리가 이 교차 데이터를 역산하면 오차율 0%의 무결점 매핑 테이블을 구축할 수 있습니다.

### 🛠️ 구현 단계 (Action Items)

1. **네이버 실거래가 내역 스크래퍼 제작 (역추적용)**
   - 1회성 시드(Seed) 스크립트 구축.
   - 네이버 개별 평형(ptpNo) 단위로 진입한 후, 노출되는 **과거 실거래가 내역 (거래일자, 거래금액, 층수)** 샘플(1~2건)을 수집.

2. **국토부 DB 십자 대조 (Cross-Validation)**
   - 확보한 네이버발 실거래가 샘플(날짜/층/가격)을 기존 구축된 국토부 DB(`rtms_transactions`) 기준으로 `SELECT` 쿼리 조인.
   - 유일하게 100% 조건이 일치하는 국토부 레코드를 식별하여 국토부 측의 `전용면적(match_key_area)`을 추출.

3. **무결점 매핑 테이블(`pyeong_map`) 구성**
   - 위 조작을 통해 `[국토부 기준 전용면적] ↔ [네이버 측 공급면적(pyeongNm) + ptpNo]` 형태의 정적 참조 테이블 완성.
   - 이를 DB에 업로드하거나 JSON으로 고정.

4. **파이프라인 결합 및 간소화**
   - 일일 파이프라인(`19_build_json_db.py`, `20_mdd_bridge.py`) 생성 시 방금 완성된 확정 매핑 테이블을 최우선 기준으로 따르도록 로직 변경.
   - 현재 오차를 보정하기 위해 임시 탑재해둔 '인접 면적 병합(Merge)' 로직을 제거하여 하드코딩된 단일 기준으로 통합.

> **기대 효과:** 이 아키텍처가 도입되면 아무리 복잡한 평형 분할을 가진 단지라도, 공급면적 표기 누락이나 타입이 이중으로 갈라지는 프론트엔드 버그가 원천 방지됩니다.


## 📈 [Phase 2] SNS Growth 마케팅 자동화 파이프라인 구축 (Next Step)
**(2026-08-03 업데이트)**

### 💡 아이디어 개요
10년 치 데이터베이스 기반 정밀 매핑 및 매일 새벽 파이프라인의 안정성이 100% 검증된 후 진행될 '가입자 유도 및 활성화' 페이즈입니다. 
기존에 성공적으로 구축했던 '전래동화 유튜브 쇼츠 자동화 파이프라인(P12)'의 노하우를 바탕으로, 프롭테크 SNS 마케팅 또한 AI 에이전트 전담 자동화 공장으로 변환합니다.

### 🛠️ 구현 단계 (Action Items)
1. **자동 쇼츠/릴스 제작 (YouTube/Instagram)**
   - 매일 DB를 스캔하여 '오늘 서울 기준 가장 많이 하락(MDD)한 아파트 Top 3' 추출.
   - AI를 통한 후킹 대본 자동 생성, TTS 및 템플릿(Remotion/FFmpeg) 병합 후 자동 업로드.
2. **마켓 브리핑 뉴스 채널 운영 (Threads/Telegram)**
   - 데일리 시장 투자 심리 점수(상승/하락) 메트릭 산출 및 브리핑 포스팅 자동 발생.
   - 유저 유입을 위한 lantertainer.com 랜딩 URL 삽입.
3. **타겟 오디언스 소통 (스마트 댓글 봇)**
   - 인스타그램, 트레드에서 #아파트매매, #부동산재테크 해시태그 게시물 감지.
   - 스팸이 아닌 해당 게시물 맥락(주제, 지역)에 맞는 부동산 인사이트 통계(예: '강동구 그라시움 최근 호가 -30% 진입 기록' 등)를 댓글로 자동 반영하여 유기적 유입 극대화.


### ?? ���� ���� (Next Steps - 2026-08-04)
1. **���̵�� �޴� �� ����� ���ġ**: ���� '�ŷ��� ���� ���' �ٷ� �Ʒ��� [��Ȳ ����Ʈ �Խ���] �� �޴� ������ ���ġ.
2. **������ ���� ���� (Phase 3)**: Vercel ��Ÿ���� ��ũ ��� �� ������Ʈ ���� �ϵ��ڵ� �ϰ� ��ü.
3. **���ɴ��� ����ȣ�� Ʈ��ŷ ����ȭ ����**: 50�� ���� ����Ʈ �����Ͽ��� �߻��ϴ� ���� �ð�(Scale-up) �̽� ��ȭ �� ĳ�� ���� ����.
