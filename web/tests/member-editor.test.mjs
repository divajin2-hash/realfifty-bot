import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(root+'/package.json');
const ts=require('typescript');
async function moduleAt(file,overrides={}){const source=await fs.readFile(root+'/'+file,'utf8');const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;const m={exports:{}};new Function('require','module','exports',js)((name)=>name in overrides?overrides[name]:require(name),m,m.exports);return m.exports;}
const model=await moduleAt('src/lib/member-model.ts');
const originalFetch=globalThis.fetch;
const reviewEnvNames=['REALFIFTY_REVIEW_STORE','NEXT_PUBLIC_SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY'];
const originalReviewEnv=Object.fromEntries(reviewEnvNames.map(name=>[name,process.env[name]]));
try {
 process.env.REALFIFTY_REVIEW_STORE='supabase';
 process.env.NEXT_PUBLIC_SUPABASE_URL='https://example.supabase.co';
 const cloudReview=await moduleAt('src/lib/factcheck-review.ts',{'./factcheck-data':{auditRoot:()=>{throw new Error('Cloud review must not access files');}}});
 for(const key of ['sb_secret_test_only','eyJ.test.legacy']) {
  process.env.SUPABASE_SERVICE_ROLE_KEY=key;
  const calls=[];
  globalThis.fetch=async (url,options)=>{calls.push({url,options});return new Response('[]',{status:200});};
  await cloudReview.readPublications();
  await cloudReview.saveReview({job_id:'test',reviewed_at:'2026-09-16T00:00:00Z'});
  assert.equal(calls.length,2);
  for(const {options} of calls){assert.equal(options.headers.apikey,key);assert.equal(options.headers.Authorization,key.startsWith('eyJ')?`Bearer ${key}`:undefined);assert.equal(options.cache,'no-store');}
 }
 console.log('PASS: 새 서버 키·레거시 키의 클라우드 읽기/쓰기 인증 헤더');
} finally {
 globalThis.fetch=originalFetch;
 for(const name of reviewEnvNames){if(originalReviewEnv[name]===undefined)delete process.env[name];else process.env[name]=originalReviewEnv[name];}
}
for(const x of ['https://evil.test','//evil.test','/\\evil.test','/\r\nevil.test',null])assert.equal(model.safeReturn(x),'/account');
assert.equal(model.safeReturn('/complex?id=abc&tab=discussion#discussion'),'/complex?id=abc&tab=discussion#discussion');
console.log('PASS: 로그인 복귀 주소 외부 이동 차단');
const tmp=await fs.mkdtemp(path.join(os.tmpdir(),'rf-review-test-'));
try{
 const review=await moduleAt('src/lib/factcheck-review.ts',{'./factcheck-data':{auditRoot:()=>tmp}});
 const result={job_id:'a'.repeat(32),status:'collected',verdict:'TEST',stats:{up:3}};
 const hash=review.resultHash(result);
 await review.saveReview({job_id:result.job_id,status:'published',result,fingerprint:hash,reviewed_at:'2026-09-16T00:00:00Z'});
 result.stats.up=99;
 assert.notEqual(review.resultHash(result),hash);
 assert.equal((await review.readPublications())[0].result.stats.up,3);
 await review.saveReview({job_id:result.job_id,status:'held',result,fingerprint:review.resultHash(result),reviewed_at:'2026-09-16T01:00:00Z'});
 assert.equal((await review.readPublications()).filter(r=>r.status==='published').length,0);
 assert.equal((await fs.readdir(path.join(tmp,'reviews/history'))).length,2);
 console.log('PASS: 승인 근거 버전 보존, 보류 전환, 검토 이력');
}finally{const resolved=path.resolve(tmp);assert.equal(path.dirname(resolved),path.resolve(os.tmpdir()));assert.ok(path.basename(resolved).startsWith('rf-review-test-'));await fs.rm(resolved,{recursive:true,force:true});}
const admin=await moduleAt('src/lib/admin-access.ts',{'./member-server':{sameOrigin:()=>true,memberIdentity:async()=>null}});
const old=process.env.NODE_ENV;process.env.NODE_ENV='production';process.env.REALFIFTY_LOCAL_ADMIN='true';assert.equal(await admin.adminAccess(new Request('http://localhost/api/admin/factcheck')),null);process.env.NODE_ENV=old;
console.log('PASS: production에서 로컬 운영자 예외 차단');
for(const [url,options,status] of [
 ['/api/member',{},401],['/api/member',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'},401],
 ['/api/admin/factcheck',{headers:{Origin:'https://untrusted.example'}},403],
 ['/api/factcheck',{method:'POST',headers:{Origin:'https://untrusted.example','Content-Type':'application/json'},body:'{}'},403]
]){const r=await fetch('http://localhost:3000'+url,options);assert.equal(r.status,status,url);}
console.log('PASS: 미인증 회원 쓰기·교차 출처 운영자 요청 차단');
const news=await(await fetch('http://localhost:3000/news')).text();assert.ok(!news.includes('검증 범위 설정'));assert.ok(!news.includes('name="scope_confirmed"'));
console.log('PASS: 독자 화면에서 검증 입력 폼 제거');
