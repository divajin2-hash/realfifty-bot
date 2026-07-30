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
