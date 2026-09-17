import {after} from 'next/server';
import {memberIdentity,sameOrigin} from '@/lib/member-server';
import {kakaoIdentity,processDeletion,serviceClient} from '@/lib/account-lifecycle';
export const runtime='nodejs';
export const maxDuration=60;
export async function POST(req:Request) {
 if(!sameOrigin(req))return Response.json({error:'허용되지 않은 요청입니다.'},{status:403});
 const auth=await memberIdentity(req);
 if(!auth)return Response.json({error:'다시 로그인해 주세요.'},{status:401});
 try{
  const raw=await req.text();
  if(raw.length>200||JSON.parse(raw).confirmation!=='탈퇴')return Response.json({error:'탈퇴 확인 문구를 입력해 주세요.'},{status:400});
  const kakaoId=kakaoIdentity(auth.user);
  if(kakaoId&&!process.env.KAKAO_ADMIN_KEY)return Response.json({error:'카카오 연결 해제 설정을 준비 중입니다. 문의 이메일로 탈퇴를 요청해 주세요.'},{status:503});
  const admin=serviceClient();
  const {error}=await admin.from('rf_account_deletions').upsert({user_id:auth.user.id,kakao_id:kakaoId||null,unlink_required:!!kakaoId},{onConflict:'user_id'});
  if(error)throw error;
  // The durable queue blocks further member operations immediately and survives worker failure.
  after(async()=>{try{await processDeletion(auth.user.id);}catch{console.error('Account deletion pending; scheduled retry required.');}});
  return Response.json({ok:true,pending:true},{status:202,headers:{'Cache-Control':'no-store'}});
 }catch{return Response.json({error:'탈퇴 요청을 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.'},{status:503});}
}
