-- Private feedback: only trusted server service_role can access this table.
create table if not exists public.rf_feedback (
 id uuid primary key,
 created_at timestamptz not null default now(),
 category text not null check (category in ('데이터 오류','사용 불편','기능 제안')),
 content text not null check (char_length(content) between 10 and 3000),
 email text not null default '',
 page text not null,
 status text not null default '접수' check (status in ('접수','검토 중','반영 예정','반영 완료'))
);
alter table public.rf_feedback enable row level security;
revoke all on public.rf_feedback from anon, authenticated;
grant select, insert, update, delete on public.rf_feedback to service_role;
