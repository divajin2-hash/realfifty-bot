import {after} from 'next/server';
import {matchesSecret,serviceClient,processDeletion} from '@/lib/account-lifecycle';
export const runtime='nodejs';
export const maxDuration=60;
export async function POST(req:Request) {
 const secret=process.env.KAKAO_ADMIN_KEY;
 if(!matchesSecret(req.headers.get('authorization'),secret?`KakaoAK ${secret}`:undefined))return new Response(null,{status:401});
 const raw=await req.text();
 if(raw.length>2000)return new Response(null,{status:413});
 const params=new URLSearchParams(raw),id=params.get('user_id');
 if(params.get('app_id')!==(process.env.KAKAO_APP_ID||'1579804')||!id||!/^\d{1,30}$/.test(id))return new Response(null,{status:400});
 try{
  // One transaction resolves the trusted Auth identity and persists the deletion job.
  const {data,error}=await serviceClient(2000).rpc('rf_enqueue_kakao_unlink',{provider_id:id});
  if(error)throw error;
  if(data)after(async()=>{try{await processDeletion(data);}catch{console.error('Kakao unlink deletion pending; scheduled retry required.');}});
  return new Response(null,{status:200});
 }catch{
  // Fail visibly when durable receipt was impossible; never acknowledge a lost request.
  console.error('Kakao unlink queue unavailable.');
  return new Response(null,{status:503});
 }
}
