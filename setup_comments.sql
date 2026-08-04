-- Supabase SQL Editor 에 복사/붙여넣기 후 실행하세요.

CREATE TABLE IF NOT EXISTS public.report_comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  report_date VARCHAR(20) NOT NULL,
  user_name VARCHAR(50) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 누구나 조회 및 작성할 수 있도록 RLS (보안 정책) 해제 혹은 설정
-- 여기서는 사이트 초기 빌드를 위해 RLS를 비활성화 하거나 간단하게 엽니다.
ALTER TABLE public.report_comments DISABLE ROW LEVEL SECURITY;
