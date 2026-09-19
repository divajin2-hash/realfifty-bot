-- RealFifty V2 데이터베이스 업그레이드 스크립트
-- 이 쿼리를 Supabase의 [SQL Editor] 메뉴에 통째로 붙여넣고 "RUN" 하시면 됩니다.

-- 1. pyeong_stats 테이블 (실시간 터미널 렌더링용) 확충
ALTER TABLE public.pyeong_stats ADD COLUMN normal_lowest_ask BIGINT DEFAULT 0; -- 1층/탑층 제외 진성 최저가
ALTER TABLE public.pyeong_stats ADD COLUMN sale_count INT DEFAULT 0;           -- 매매 매물 총 갯수
ALTER TABLE public.pyeong_stats ADD COLUMN jeonse_count INT DEFAULT 0;         -- 전세 매물 총 갯수
ALTER TABLE public.pyeong_stats ADD COLUMN jeonse_lowest_ask BIGINT DEFAULT 0; -- 전세 최저가
ALTER TABLE public.pyeong_stats ADD COLUMN top_5_listings JSONB DEFAULT '[]'::jsonb; -- Top 5 매물 상세 정보 (JSON)
ALTER TABLE public.pyeong_stats ADD COLUMN jeonse_rate REAL DEFAULT 0.0;       -- 전세가율 (%)

-- 2. daily_history 테이블 (시계열 차트 및 프리미엄 알림용) 확충
ALTER TABLE public.daily_history ADD COLUMN normal_lowest_ask BIGINT DEFAULT 0; 
ALTER TABLE public.daily_history ADD COLUMN sale_count INT DEFAULT 0;
ALTER TABLE public.daily_history ADD COLUMN jeonse_count INT DEFAULT 0;
ALTER TABLE public.daily_history ADD COLUMN jeonse_lowest_ask BIGINT DEFAULT 0;
ALTER TABLE public.daily_history ADD COLUMN jeonse_rate REAL DEFAULT 0.0;

-- 3. (옵션) 혹시 모를 에러 방지를 위해 기존 뷰(View)나 쿼리에 영향이 없도록 기본값 처리를 완료했습니다.
SELECT 'V2 Schema Upgrade Completed Successfully!' as status;
