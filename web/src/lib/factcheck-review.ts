import fs from 'node:fs/promises';import path from 'node:path';import {createHash,randomUUID} from 'node:crypto';import {auditRoot} from './factcheck-data';import type {AuditResult} from './factcheck-model';
export type Publication={job_id:string;status:'published'|'held'|'rejected';summary:string;note:string;reviewer:string;reviewed_at:string;fingerprint:string;result:AuditResult};
export const resultHash=(r:AuditResult)=>createHash('sha256').update(JSON.stringify(r)).digest('hex');
export const cloudReviews = () => process.env.VERCEL === '1' || process.env.REALFIFTY_REVIEW_STORE === 'supabase';
async function reviewStore(method: string, value?: Publication) {
 const url=process.env.NEXT_PUBLIC_SUPABASE_URL, key=process.env.SUPABASE_SERVICE_ROLE_KEY;
 if(!url||!key)throw new Error('팩트체크 저장소 설정이 필요합니다.');
 const response=await fetch(`${url}/rest/v1/rf_factcheck_reviews${method==='GET'?'?select=document&order=reviewed_at.desc':'?on_conflict=job_id'}`,{
 method,headers:{apikey:key,...(key.startsWith('eyJ')?{Authorization:`Bearer ${key}`} : {}),'Content-Type':'application/json',Prefer:'resolution=merge-duplicates'},
 ...(value?{body:JSON.stringify({job_id:value.job_id,reviewed_at:value.reviewed_at,document:value})}:{}),cache:'no-store',signal:AbortSignal.timeout(10000)});
 if(!response.ok)throw new Error('팩트체크 저장소에 연결하지 못했습니다.');
 return method==='GET' ? await response.json() as {document:Publication}[] : [];
}
export async function readPublications(){if(cloudReviews())return (await reviewStore('GET')).map(x=>x.document);const root=path.join(auditRoot(),'reviews');const out:Publication[]=[];try{for(const f of await fs.readdir(root)){if(!/^[a-f0-9]{32}\.json$/.test(f))continue;try{out.push(JSON.parse(await fs.readFile(path.join(root,f),'utf8')));}catch{}}}catch{}return out.sort((a,b)=>b.reviewed_at.localeCompare(a.reviewed_at));}
export async function saveReview(value:Publication){if(cloudReviews()){await reviewStore('POST',value);return;}const root=path.join(auditRoot(),'reviews');await fs.mkdir(root,{recursive:true});const lock=path.join(root,`${value.job_id}.lock`);try{await fs.mkdir(lock);}catch{throw new Error('다른 검토가 진행 중입니다. 다시 확인하세요.');}try{const history=path.join(root,'history');await fs.mkdir(history,{recursive:true});await fs.writeFile(path.join(history,`${value.job_id}-${randomUUID()}.json`),JSON.stringify(value,null,2),'utf8');const tmp=path.join(root,`${value.job_id}.${randomUUID()}.tmp`);await fs.writeFile(tmp,JSON.stringify(value,null,2),'utf8');await fs.rename(tmp,path.join(root,`${value.job_id}.json`));}finally{await fs.rmdir(lock);}}
