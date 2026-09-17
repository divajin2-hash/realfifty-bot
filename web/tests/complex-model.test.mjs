import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import test from 'node:test';
import ts from 'typescript';
import Module from 'node:module';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = fs.readFileSync(path.join(root, 'src/lib/complex-model.ts'), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
const mod = new Module('complex-model');
mod._compile(compiled, 'complex-model.cjs');
const model = mod.exports;

test('원 단위 가격을 억으로 환산하고 누락값을 가격으로 표현하지 않는다', () => {
  assert.equal(model.price(3451000000), '34.51억');
  assert.equal(model.price(0), '미수집');
  assert.equal(model.price(null), '미수집');
});

test('호가가 없으면 -100%를 만들지 않고 양수·음수 괴리를 보존한다', () => {
  assert.equal(model.change(0, 100), null);
  assert.equal(model.change(100, 0), null);
  assert.equal(model.change(NaN, 100), null);
  assert.equal(model.percent(model.change(90, 100)), '-10.0%');
  assert.equal(model.percent(model.change(110, 100)), '+10.0%');
});

test('한국 시간 자정 직후에도 계약 경과일이 정확하다', () => {
  assert.equal(model.daysSince('2026-07-09', '2026-09-15T15:06:00Z'), 69);
  assert.equal(model.daysSince('2027-01-01', '2026-09-15T15:06:00Z'), null);
  assert.equal(model.daysSince(undefined, '2026-09-16'), null);
});

test('대표 평형 선택은 빈 배열과 최근 실거래가 없는 타입을 처리한다', () => {
  assert.equal(model.representative([], '2026-09-16'), null);
  const stale = { match_key_area: 84, highest_deal_price: 100, current_lowest_ask: 90, recent_deal_absolute: { date: '2020-01-01', price: 80 } };
  const fresh = { ...stale, match_key_area: 85, recent_deal_absolute: { date: '2026-09-01', price: 85 } };
  assert.equal(model.representative([stale, fresh], '2026-09-16'), fresh);
});

test('원본 전체 평형의 선택 키가 유일하고 미수집 호가를 비교에서 제외한다', () => {
  const groups = JSON.parse(fs.readFileSync(path.join(root, 'src/data/kb50_stats.json'), 'utf8'));
  for (const group of groups) {
    assert.equal(new Set(group.stats.map(model.areaKey)).size, group.stats.length, group.complex.name);
    for (const stat of group.stats) {
      if (!model.positive(stat.current_lowest_ask)) assert.equal(model.change(stat.current_lowest_ask, stat.highest_deal_price), null);
    }
  }
});

test('배포 파일 시각에 의존하지 않고 스냅샷 기준일로 50개 단지를 비교한다', async () => {
  const raw = JSON.parse(fs.readFileSync(path.join(root, 'src/data/kb50_stats.json'), 'utf8'));
  const loader = new Module('complex-data');
  loader.require = (id) => {
    if (id === 'react') return { cache: fn => fn };
    if (id === './complex-model') return model;
    if (id === 'node:fs/promises') return { readFile: async () => JSON.stringify(raw), stat: async () => ({mtime:new Date('2018-10-20')}) };
    return mod.require(id);
  };
  loader._compile(ts.transpileModule(fs.readFileSync(path.join(root,'src/lib/complex-data.ts'),'utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText,'complex-data.cjs');
  const result = await loader.exports.readUniverse();
  assert.equal(result.updatedAt, raw[0].generated_at);
  assert.equal(result.summaries.length,50);
  assert.ok(result.summaries.filter(s => model.daysSince(s.representative?.recent_deal_absolute?.date,result.updatedAt) !== null).length > 0);
  for (const group of raw) delete group.generated_at;
  await assert.rejects(loader.exports.readUniverse(), /timestamp/);
});
