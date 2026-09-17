import {randomUUID} from 'node:crypto';
import {feedbackStore} from '@/lib/feedback-store';
export const runtime='nodejs';
const attempts=new Map<string,number>();
export async function POST(req:Request){
 if(req.headers.get('origin')!==new URL(req.url).origin)return Response.json({error:'허용되지 않은 요청입니다.'},{status:403});
 const ip=req.headers.get('x-forwarded-for')?.split(',')[0]||'local';
 const now=Date.now();for(const [k,t] of attempts)if(now-t>60000)attempts.delete(k);
 if(attempts.has(ip))return Response.json({error:'잠시 후 다시 접수해 주세요.'},{status:429});
 attempts.set(ip,now);
 const text=await req.text();if(text.length>8000)return Response.json({error:'내용이 너무 깁니다.'},{status:413});
 let b;try{b=JSON.parse(text);}catch{return Response.json({error:'잘못된 입력입니다.'},{status:400});}
 if(b.website)return Response.json({error:'접수할 수 없습니다.'},{status:400});
 const content=String(b.content||'').trim(),email=String(b.email||'').trim(),page=String(b.page||'');
 if(!['데이터 오류','사용 불편','기능 제안'].includes(b.category)||content.length<10||content.length>3000||email.length>254||(email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))||!b.consent||page.length>300||!page.startsWith('/'))return Response.json({error:'분류·내용(10~3,000자)·이메일과 개인정보 안내 동의를 확인해 주세요.'},{status:400});
 try{const id=randomUUID();await feedbackStore('POST',{id,created_at:new Date().toISOString(),category:b.category,content,email,page,status:'접수'});return Response.json({ok:true,id},{status:201});}catch{return Response.json({error:'접수 저장에 실패했습니다. 다시 시도하거나 하단 문의 이메일을 이용해 주세요.'},{status:503});}
}
