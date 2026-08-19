-- 기존 community_comments 테이블에 작성자 닉네임 컬럼 추가
ALTER TABLE public.community_comments ADD COLUMN author_name TEXT;

-- 기존에 저장된(방금 봇이 남긴) 데이터가 있다면 기본값 채워넣기
UPDATE public.community_comments SET author_name = '익명유저' WHERE author_name IS NULL;
