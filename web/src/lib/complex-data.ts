import fs from 'node:fs/promises';
import path from 'node:path';
import { cache } from 'react';
import { positive, representative, type ComplexGroup, type ComplexDetail, type ComplexSummary } from './complex-model';

export const readUniverse = cache(async () => {
  const file = path.join(process.cwd(), 'src/data/kb50_stats.json');
  const body = await fs.readFile(file, 'utf8');
  const groups = JSON.parse(body) as ComplexGroup[];
  if (!Array.isArray(groups)) throw new Error('Invalid complex data');
  const updatedAt = groups[0]?.generated_at;
  if (!updatedAt || !Number.isFinite(Date.parse(updatedAt)) || groups.some(g => g.generated_at !== updatedAt)) {
    throw new Error('Missing or inconsistent data generation timestamp');
  }
  const summaries: ComplexSummary[] = groups.map(g => {
    const rep = representative(g.stats, updatedAt);
    return {
      ...g.complex, typeCount: g.stats.length,
      representative: rep ? {
        match_key_area: rep.match_key_area, pyeong_name: rep.pyeong_name,
        naver_ptp_no: rep.naver_ptp_no, exclusive_area: rep.exclusive_area, supply_area: rep.supply_area,
        highest_deal_price: rep.highest_deal_price, recent_deal_absolute: rep.recent_deal_absolute,
        current_lowest_ask: rep.current_lowest_ask,
      } : null,
      volume: new Set(g.stats.flatMap(s => (s.month_deals || []).map(t => t.id || `${s.exclusive_area}:${t.date}:${t.price}:${t.floor}:${t.type}`))).size,
      availableTypes: g.stats.filter(s => positive(s.current_lowest_ask)).length,
    };
  }).sort((a, b) => a.name.localeCompare(b.name, 'ko'));
  return { groups, summaries, updatedAt };
});

export async function readComplex(id: string): Promise<ComplexDetail | null> {
  const { groups, updatedAt } = await readUniverse();
  const group = groups.find(g => g.complex.id === id);
  if (!group) return null;
  let chart: ComplexDetail['chart'] = {};
  let reportDate: string | null = null;
  try { chart = JSON.parse(await fs.readFile(path.join(process.cwd(), 'public/chart_data', `${group.complex.id}.json`), 'utf8')); } catch { /* History is optional. */ }
  try {
    const reports = await fs.readdir(path.join(process.cwd(), 'src/data/reports'));
    reportDate = reports.filter(f => /^report_\d{4}-\d{2}-\d{2}\.md$/.test(f)).sort().at(-1)?.slice(7, 17) || null;
  } catch { /* Optional report. */ }
  return { ...group, chart, updatedAt, reportDate };
}
