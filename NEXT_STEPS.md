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
