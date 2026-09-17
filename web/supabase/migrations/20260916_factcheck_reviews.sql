-- Apply after review. No existing tables or records are modified.
begin;
create table if not exists public.rf_factcheck_reviews (
 job_id text primary key check (job_id ~ '^[a-f0-9]{32}$'),
 reviewed_at timestamptz not null,
 document jsonb not null check (document->>'status' in ('published','held','rejected'))
);
create table if not exists public.rf_factcheck_review_history (
 id bigint generated always as identity primary key,
 recorded_at timestamptz not null default now(),
 job_id text not null,
 document jsonb not null
);
alter table public.rf_factcheck_reviews enable row level security;
alter table public.rf_factcheck_review_history enable row level security;
revoke all on public.rf_factcheck_reviews, public.rf_factcheck_review_history from anon, authenticated;
grant all on public.rf_factcheck_reviews, public.rf_factcheck_review_history to service_role;
grant usage, select on sequence public.rf_factcheck_review_history_id_seq to service_role;
create or replace function public.rf_record_review_history() returns trigger
language plpgsql set search_path = '' as $$
begin
 insert into public.rf_factcheck_review_history(job_id, document) values(new.job_id, new.document);
 return new;
end;
$$;
revoke all on function public.rf_record_review_history() from public;
drop trigger if exists rf_review_history on public.rf_factcheck_reviews;
create trigger rf_review_history after insert or update on public.rf_factcheck_reviews
for each row execute function public.rf_record_review_history();
commit;
