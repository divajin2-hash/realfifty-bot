-- 1. 커뮤니티 투표 및 댓글을 저장할 테이블 생성
CREATE TABLE public.community_comments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    complex_id UUID REFERENCES public.complexes(id) ON DELETE CASCADE, -- 해당 평형/단지의 ID (complexes 테이블 참조)
    user_id UUID, -- 향후 실제 유저 로그인 연동을 대비한 필드 (현재는 bot이므로 null)
    is_bot BOOLEAN DEFAULT true, -- 봇 여부 확인 (실제 유저와 통계 분리용)
    persona_type TEXT, -- 어떤 봇인지 구분 (예: 'extreme_bull', 'extreme_bear', 'quant', 'real_demand' 등)
    vote TEXT, -- 'bull' (상승), 'bear' (하락), 'neutral' (중립/관망)
    content TEXT NOT NULL, -- 작성된 댓글 내용
    created_at TIMESTAMPTZ DEFAULT NOW(), -- 작성 시간
    parent_id UUID REFERENCES public.community_comments(id) ON DELETE CASCADE -- 대댓글 구조를 위한 자기 참조 (nullable)
);

-- 2. 검색 성능 향상을 위한 인덱스 생성
CREATE INDEX idx_community_comments_complex_id ON public.community_comments(complex_id);
CREATE INDEX idx_community_comments_created_at ON public.community_comments(created_at DESC);
CREATE INDEX idx_community_comments_vote ON public.community_comments(vote);

-- 3. Row Level Security (RLS) 설정 (선택 사항 - API에서 직접 밀어넣으므로 퍼블릭 읽기 허용)
ALTER TABLE public.community_comments ENABLE ROW LEVEL SECURITY;

-- 누구나 댓글을 읽을 수 있도록 허용
CREATE POLICY "Allow public read access on community_comments" 
ON public.community_comments FOR SELECT 
USING (true);

-- API(서비스 역할) 또는 인증된 유저만 글을 작성할 수 있도록 허용
CREATE POLICY "Allow insert for authenticated users or service role" 
ON public.community_comments FOR INSERT 
WITH CHECK (true); -- 현재는 편의상 모두 허용하지만, 추후 auth.uid() = user_id 로 변경 가능
