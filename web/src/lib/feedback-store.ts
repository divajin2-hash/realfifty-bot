import 'server-only';
import fs from 'node:fs/promises';
import path from 'node:path';
export type Feedback={id:string;created_at:string;category:string;content:string;email:string;page:string;status:string};
const root=path.join(process.cwd(),'.local-feedback');
export async function feedbackStore(method:'GET'|'POST'|'PATCH', value?:Partial<Feedback>){
 if(process.env.VERCEL==='1'||process.env.REALFIFTY_FEEDBACK_STORE==='supabase'){
 const url=process.env.NEXT_PUBLIC_SUPABASE_URL,key=process.env.SUPABASE_SERVICE_ROLE_KEY;
 if(!url||!key)throw new Error('접수 저장소가 준비되지 않았습니다. 문의 이메일을 이용해 주세요.');
 const cutoff=new Date(Date.now()-90*86400000).toISOString();
 const cleanup=await fetch(`${url}/rest/v1/rf_feedback?created_at=lt.${encodeURIComponent(cutoff)}`,{method:'DELETE',headers:{apikey:key,...(key.startsWith('eyJ')?{Authorization:`Bearer ${key}`} :{})},signal:AbortSignal.timeout(10000)});
 if(!cleanup.ok)throw new Error('저장소 유지 관리에 실패했습니다.');
 const suffix=method==='GET'?'?select=*&order=created_at.desc&limit=200':method==='PATCH'?`?id=eq.${value?.id}`:'';
 const r=await fetch(`${url}/rest/v1/rf_feedback${suffix}`,{method,headers:{apikey:key,...(key.startsWith('eyJ')?{Authorization:`Bearer ${key}`} :{}),'Content-Type':'application/json'},body:method==='GET'?undefined:JSON.stringify(value),cache:'no-store',signal:AbortSignal.timeout(10000)});
 if(!r.ok)throw new Error('접수 저장소 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.');
 return method==='GET'?await r.json() as Feedback[]:[];
 }
 await fs.mkdir(root,{recursive:true});
 for(const f of await fs.readdir(root)){if(!/^[a-f0-9-]{36}\.json$/.test(f))continue;const old=JSON.parse(await fs.readFile(path.join(root,f),'utf8'));if(Date.parse(old.created_at)<Date.now()-90*86400000)await fs.unlink(path.join(root,f));}
 if(method==='GET'){const rows:Feedback[]=[];for(const f of await fs.readdir(root)){if(/^[a-f0-9-]{36}\.json$/.test(f))rows.push(JSON.parse(await fs.readFile(path.join(root,f),'utf8')));}return rows.sort((a,b)=>b.created_at.localeCompare(a.created_at)).slice(0,200);}
 const file=path.join(root,`${value?.id}.json`);
 const row=method==='PATCH'?{...JSON.parse(await fs.readFile(file,'utf8')),...value}:value;
 await fs.writeFile(file,JSON.stringify(row),'utf8');return [];
}
