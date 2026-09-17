begin;
-- Retained only until processing succeeds; no FK so a completed Auth delete can be retried safely.
create table if not exists public.rf_account_deletions (
 user_id uuid primary key,
 kakao_id text,
 unlink_required boolean not null default false,
 requested_at timestamptz not null default now()
);
alter table public.rf_account_deletions enable row level security;
revoke all on public.rf_account_deletions from public,anon,authenticated;
grant select,insert,update,delete on public.rf_account_deletions to service_role;

create or replace function public.rf_member_active() returns boolean
language sql stable security definer set search_path='' as $$
 select exists(select 1 from auth.users u where u.id=auth.uid())
 and not exists(select 1 from public.rf_account_deletions d where d.user_id=auth.uid());
$$;
revoke all on function public.rf_member_active() from public,anon;
grant execute on function public.rf_member_active() to authenticated,service_role;

create or replace function public.rf_enqueue_kakao_unlink(provider_id text) returns uuid
language plpgsql security definer set search_path='' as $$
declare target uuid;
begin
 select user_id into target from auth.identities where provider='kakao' and auth.identities.provider_id=$1;
 if target is null then return null; end if;
 insert into public.rf_account_deletions(user_id,kakao_id,unlink_required) values(target,$1,false)
 on conflict(user_id) do update set unlink_required=false;
 return target;
end;
$$;
revoke all on function public.rf_enqueue_kakao_unlink(text) from public,anon,authenticated;
grant execute on function public.rf_enqueue_kakao_unlink(text) to service_role;

do $$ declare t text; begin
 foreach t in array array['rf_profiles','rf_watchlist','rf_saved_reports','rf_alert_rules','rf_notifications','rf_member_opinions'] loop
  execute format('drop policy if exists active_member on public.%I',t);
  execute format('create policy active_member on public.%I as restrictive for all to authenticated using ((select public.rf_member_active())) with check ((select public.rf_member_active()))',t);
 end loop;
end $$;
-- Hide opinions as soon as withdrawal is queued, including from signed-out readers.
create or replace function public.rf_author_active(author_id uuid) returns boolean
language sql stable security definer set search_path='' as $$
 select not exists(select 1 from public.rf_account_deletions d where d.user_id=author_id);
$$;
revoke all on function public.rf_author_active(uuid) from public;
grant execute on function public.rf_author_active(uuid) to anon,authenticated,service_role;
drop policy if exists public_feed on public.rf_member_opinions;
create policy public_feed on public.rf_member_opinions for select to anon using (
 public.rf_author_active(user_id)
);
commit;
