import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),ts=require('typescript');
async function load(file,overrides={}){
 const source=await fs.readFile(new URL('../'+file,import.meta.url),'utf8');
 const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 const module={exports:{}};new Function('require','module','exports',js)(name=>name in overrides?overrides[name]:require(name),module,module.exports);return module.exports;
}
const lifecycle=await load('src/lib/account-lifecycle.ts');
assert.equal(lifecycle.matchesSecret(null,undefined),false);
assert.equal(lifecycle.matchesSecret('same','same'),true);
assert.equal(lifecycle.matchesSecret('wrong','same'),false);
assert.equal(lifecycle.kakaoIdentity({user_metadata:{provider_id:'attacker'},identities:[{provider:'kakao',id:'trusted'}]}),'trusted');
console.log('PASS: webhook authentication fails closed; target comes from Auth identity');
const previousKey=process.env.KAKAO_ADMIN_KEY,previousFetch=globalThis.fetch;
process.env.KAKAO_ADMIN_KEY='test-only';
try{
 globalThis.fetch=async()=>Response.json({code:-101},{status:400});await lifecycle.unlinkKakao('123');
 globalThis.fetch=async()=>Response.json({id:456});await assert.rejects(()=>lifecycle.unlinkKakao('123'));
 globalThis.fetch=async()=>Response.json({code:-401},{status:401});await assert.rejects(()=>lifecycle.unlinkKakao('123'));
 globalThis.fetch=async()=>Response.json({id:123});await lifecycle.unlinkKakao('123');
 console.log('PASS: unlink retries accept already-unlinked user, reject wrong user and authentication failure');
}finally{globalThis.fetch=previousFetch;if(previousKey===undefined)delete process.env.KAKAO_ADMIN_KEY;else process.env.KAKAO_ADMIN_KEY=previousKey;}
let authenticated=true,sameOrigin=true,queued=[],afterTasks=[];
const withdrawal=await load('src/app/api/member/withdraw/route.ts',{
 'next/server':{after:fn=>afterTasks.push(fn)},
 '@/lib/member-server':{sameOrigin:()=>sameOrigin,memberIdentity:async()=>authenticated?{user:{id:'current-user'}}:null},
 '@/lib/account-lifecycle':{kakaoIdentity:()=>undefined,processDeletion:async()=>{},serviceClient:()=>({from:()=>({upsert:async row=>{queued.push(row);return {error:null};}})})}
});
const request=body=>new Request('https://example.test/api/member/withdraw',{method:'POST',body:JSON.stringify(body)});
sameOrigin=false;assert.equal((await withdrawal.POST(request({confirmation:'탈퇴'}))).status,403);
sameOrigin=true;authenticated=false;assert.equal((await withdrawal.POST(request({confirmation:'탈퇴'}))).status,401);
authenticated=true;assert.equal((await withdrawal.POST(request({confirmation:'no'}))).status,400);assert.equal(queued.length,0);
assert.equal((await withdrawal.POST(request({confirmation:'탈퇴',user_id:'victim'}))).status,202);
assert.equal(queued[0].user_id,'current-user');assert.equal(afterTasks.length,1);
console.log('PASS: withdrawal requires auth, same origin and confirmation; ignores client-supplied user id');
let rpcCalls=0;
const webhook=await load('src/app/api/auth/kakao/unlink/route.ts',{
 'next/server':{after:()=>{}},
 '@/lib/account-lifecycle':{matchesSecret:lifecycle.matchesSecret,processDeletion:async()=>{},serviceClient:()=>({rpc:async()=>{rpcCalls++;return {data:null,error:null};}})}
});
process.env.KAKAO_ADMIN_KEY='test-only';
try{
 const req=(auth,body)=>new Request('https://example.test/api/auth/kakao/unlink',{method:'POST',headers:auth?{authorization:auth}:{},body});
 assert.equal((await webhook.POST(req(null,'app_id=1579804&user_id=123'))).status,401);
 assert.equal((await webhook.POST(req('KakaoAK test-only','app_id=wrong&user_id=123'))).status,400);
 assert.equal((await webhook.POST(req('KakaoAK test-only','app_id=1579804&user_id=invalid'))).status,400);
 assert.equal(rpcCalls,0);
 assert.equal((await webhook.POST(req('KakaoAK test-only','app_id=1579804&user_id=123'))).status,200);
 assert.equal(rpcCalls,1);
 console.log('PASS: forged/wrong-app webhook cannot enqueue; unknown valid user is idempotent');
}finally{if(previousKey===undefined)delete process.env.KAKAO_ADMIN_KEY;else process.env.KAKAO_ADMIN_KEY=previousKey;}
