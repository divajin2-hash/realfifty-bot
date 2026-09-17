import fs from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';
import ts from 'typescript';
import Module from 'node:module';
const mod = new Module('market-reading');
mod._compile(ts.transpileModule(fs.readFileSync('src/lib/market-reading.ts','utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,'market-reading.cjs');
const {compareVolume}=mod.exports;
const stamp='2026-09-17T04:00:00Z';
const trade=(id,date)=>({id,date,price:100});
const group=(trades,s=stamp)=>[{generated_at:s,complex:{id:'a'},stats:[{all_trades_history:trades}]}];
const run=(g)=>compareVolume(g,new Date(stamp));
test('same-day intervals and shared type deduplication',()=>{
 const g=group([trade('a','2026-08-16'),trade('b','2026-08-17'),trade('c','2026-09-16'),trade('d','2026-09-17')]);
 g[0].stats.push(g[0].stats[0]); const r=run(g);
 assert.equal(r.previous,1); assert.equal(r.current,1); assert.equal(r.end,'2026-09-16');
});
test('missing history, ids, stale or inconsistent data fail closed',()=>{
 assert.equal(run(group([{date:'2026-09-10'}])),null);
 assert.equal(run([{...group([])[0],stats:[{}]}]),null);
 assert.equal(run(group([],'2026-09-01T00:00:00Z')),null);
 assert.equal(run([...group([]),...group([],'2026-09-16T04:00:00Z')]),null);
});
test('zero denominator is not a percent',()=>assert.equal(run(group([])).change,null));
test('first day and shorter previous month',()=>{
 const first='2026-09-30T16:00:00Z'; assert.equal(compareVolume(group([],first),new Date(first)),null);
 const march='2026-03-31T04:00:00Z'; const r=compareVolume(group([],march),new Date(march));
 assert.equal(r.end,'2026-03-28'); assert.equal(r.previousEnd,'2026-02-28');
});
test('real dataset has a valid comparison at its export time',()=>{
 const g=JSON.parse(fs.readFileSync('src/data/kb50_stats.json','utf8'));
 const r=compareVolume(g,new Date(g[0].generated_at)); assert.ok(r); console.log(JSON.stringify(r));
});
