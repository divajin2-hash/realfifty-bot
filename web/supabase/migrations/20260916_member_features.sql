-- RealFifty member features: apply to a staging Supabase project first.
-- New tables only; does not alter legacy community tables.
begin;
create table if not exists public.rf_profiles (
 user_id uuid primary key references auth.users(id) on delete cascade,
 nickname text not null check (char_length(nickname) between 2 and 20)
);
create table if not exists public.rf_watchlist (
 user_id uuid not null references auth.users(id) on delete cascade,
 complex_id text not null, label text not null,
 primary key(user_id,complex_id)
);
create table if not exists public.rf_saved_reports (
 user_id uuid not null references auth.users(id) on delete cascade,
 report_date date not null, label text not null,
 primary key(user_id,report_date)
);
create table if not exists public.rf_alert_rules (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 complex_id text not null, area text not null, label text not null,
 threshold numeric not null check(threshold between 1 and 30),
 baseline numeric not null check(baseline>0), enabled boolean not null default true,
 unique(user_id,complex_id,area)
);
create table if not exists public.rf_notifications (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 rule_id uuid not null references public.rf_alert_rules(id) on delete cascade,
 fingerprint text not null, message text not null,
 complex_id text not null, area text not null,
 created_at timestamptz not null default now(),
 unique(user_id,fingerprint)
);
create table if not exists public.rf_member_opinions (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 complex_id text not null,
 nickname text not null check(char_length(nickname) between 2 and 20),
 content text not null check(char_length(content) between 5 and 1000),
 vote text not null check(vote in ('bull','bear','neutral')),
 updated_at timestamptz not null default now(),
 unique(user_id,complex_id)
);
do $$ declare t text; begin
 foreach t in array array['rf_profiles','rf_watchlist','rf_saved_reports','rf_alert_rules','rf_notifications','rf_member_opinions'] loop
  execute format('alter table public.%I enable row level security',t);
  execute format('revoke all on public.%I from anon, authenticated',t);
  execute format('grant select,insert,update,delete on public.%I to authenticated',t);
  if not exists(select 1 from pg_policies where schemaname='public' and tablename=t and policyname='owner_only') then
   execute format('create policy owner_only on public.%I for all to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id)',t);
  end if;
 end loop;
end $$;
-- Public feed exposes neither user IDs nor email addresses.
grant select(id,complex_id,nickname,content,vote,updated_at) on public.rf_member_opinions to anon;
drop policy if exists public_feed on public.rf_member_opinions;
create policy public_feed on public.rf_member_opinions for select to anon using(true);
commit;
