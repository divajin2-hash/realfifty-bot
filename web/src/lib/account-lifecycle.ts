import {createClient, type User} from '@supabase/supabase-js';
import {timingSafeEqual} from 'node:crypto';

export function serviceClient(timeout=10000) {
 const url=process.env.NEXT_PUBLIC_SUPABASE_URL, key=process.env.SUPABASE_SERVICE_ROLE_KEY;
 if(!url||!key)throw new Error('회원 관리 설정을 확인해 주세요.');
 return createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false},global:{fetch:(url,init)=>fetch(url,{...init,signal:AbortSignal.timeout(timeout)})}});
}
export function matchesSecret(actual:string|null,expected:string|undefined) {
 if(!actual||!expected)return false;
 const a=Buffer.from(actual),b=Buffer.from(expected);
 return a.length===b.length&&timingSafeEqual(a,b);
}
export function kakaoIdentity(user:User) {
 // identities are supplied by Auth; never trust editable user_metadata for deletion targets.
 return user.identities?.find(i=>i.provider==='kakao')?.id;
}
export async function unlinkKakao(id:string) {
 const key=process.env.KAKAO_ADMIN_KEY;
 if(!key)throw new Error('카카오 연결 해제 설정을 확인해 주세요.');
 const r=await fetch('https://kapi.kakao.com/v1/user/unlink',{method:'POST',headers:{Authorization:`KakaoAK ${key}`,'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({target_id_type:'user_id',target_id:id}),signal:AbortSignal.timeout(10000),cache:'no-store'});
 const body=await r.json();
 // Kakao -101 means this user is already unlinked. A retried job may reach this state.
 if(!r.ok&&body.code!==-101)throw new Error('카카오 연결 해제에 실패했습니다. 잠시 후 다시 시도합니다.');
 if(r.ok&&String(body.id)!==id)throw new Error('카카오 연결 해제 응답을 확인해 주세요.');
}
export async function processDeletion(userId:string) {
 const admin=serviceClient();
 const {data:job,error}=await admin.from('rf_account_deletions').select('user_id,kakao_id,unlink_required').eq('user_id',userId).maybeSingle();
 if(error)throw new Error('탈퇴 요청을 조회하지 못했습니다.');
 if(!job)return;
 if(job.unlink_required&&job.kakao_id)await unlinkKakao(job.kakao_id);
 const result=await admin.auth.admin.deleteUser(job.user_id);
 if(result.error&&result.error.code!=='user_not_found')throw new Error('계정 삭제를 다시 시도합니다.');
 const removed=await admin.from('rf_account_deletions').delete().eq('user_id',job.user_id);
 if(removed.error)throw new Error('탈퇴 요청 정리가 필요합니다.');
}
export async function drainDeletions() {
 const admin=serviceClient();
 const {data,error}=await admin.from('rf_account_deletions').select('user_id').order('requested_at').limit(20);
 if(error)throw new Error('탈퇴 대기열을 조회하지 못했습니다.');
 const results=await Promise.allSettled((data||[]).map(job=>processDeletion(job.user_id)));
 const failed=results.filter(r=>r.status==='rejected').length;
 return {processed:(data?.length||0)-failed,failed};
}
