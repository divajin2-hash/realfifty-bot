import {createClient} from '@supabase/supabase-js';
import {readUniverse} from '@/lib/complex-data';
import {classifyAuthor,type Opinion,type Outlook} from '@/lib/community-model';
export const dynamic='force-dynamic';
export async function GET(request:Request){
 const {summaries}=await readUniverse();const url=new URL(request.url);const id=url.searchParams.get('complex');const kind=url.searchParams.get('kind')||'user';
 if(id&&!summaries.some(s=>s.id===id))return Response.json({error:'알 수 없는 단지입니다.'},{status:404});
 const endpoint=process.env.NEXT_PUBLIC_SUPABASE_URL,key=process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
 if(!endpoint||!key)return Response.json({comments:[],status:'unconfigured',checkedAt:new Date().toISOString()},{headers:{'Cache-Control':'no-store'}});
 try{
  const client=createClient(endpoint,key,{auth:{persistSession:false,autoRefreshToken:false},global:{fetch:(input,init)=>fetch(input,{...init,signal:AbortSignal.timeout(10000)})}});
  let query=client.from('community_comments').select('id,complex_id,author_name,content,vote,created_at,is_bot,persona_type').gte('created_at',new Date(Date.now()-30*86400000).toISOString()).order('created_at',{ascending:false}).limit(100);
  if(id)query=query.eq('complex_id',id);if(kind==='user')query=query.eq('is_bot',false);else if(kind==='ai')query=query.eq('is_bot',true);
  const {data,error}=await query;if(error)throw new Error('Read failed');
  let comments:Opinion[]=(data||[]).filter(c=>['bull','bear','neutral'].includes(c.vote)&&summaries.some(s=>s.id===c.complex_id)).map(c=>({id:String(c.id),complex_id:c.complex_id,complex_name:summaries.find(s=>s.id===c.complex_id)!.name,author_name:c.author_name||'익명',content:c.content,vote:c.vote as Outlook,created_at:c.created_at,kind:classifyAuthor(c.is_bot),generation:c.is_bot?(c.persona_type?.startsWith('evidence_v2_')?'evidence_v2':'legacy'):undefined}));
  if(kind!=='ai'){
   let memberQuery=client.from('rf_member_opinions').select('id,complex_id,nickname,content,vote,updated_at').gte('updated_at',new Date(Date.now()-30*86400000).toISOString()).order('updated_at',{ascending:false}).limit(100);
   if(id)memberQuery=memberQuery.eq('complex_id',id);
   const members=await memberQuery;
   if(!members.error)comments=[...comments,...(members.data||[]).filter(c=>summaries.some(s=>s.id===c.complex_id)).map(c=>({id:`member-${c.id}`,complex_id:c.complex_id,complex_name:summaries.find(s=>s.id===c.complex_id)!.name,author_name:c.nickname,content:c.content,vote:c.vote as Outlook,created_at:c.updated_at,kind:'user' as const}))].sort((a,b)=>b.created_at.localeCompare(a.created_at)).slice(0,100);
  }
  return Response.json({comments,status:'ok',checkedAt:new Date().toISOString(),limit:100},{headers:{'Cache-Control':'no-store'}});
 }catch{return Response.json({comments:[],status:'error',checkedAt:new Date().toISOString()},{status:503,headers:{'Cache-Control':'no-store'}});}
}
