import fs from 'node:fs/promises';
import path from 'node:path';
import { cache } from 'react';
import { readUniverse } from './complex-data';
import { areaKey, change, daysSince } from './complex-model';
export interface MacroPoint {
    month: string;
    recovery_rate: number;
    sample_count: number;
}
export const readMarket = cache(async () => {
    const universe = await readUniverse();
    const rows = universe.summaries.map(s => {
        const r = s.representative;
        return { id: s.id, name: s.name, address: s.address, area: r ? areaKey(r) : '',
            areaLabel: r ? `전용 ${r.exclusive_area || r.match_key_area}㎡` : '자료 없음',
            trade: r?.recent_deal_absolute?.price || null, tradeDate: r?.recent_deal_absolute?.date || null,
            ask: r?.current_lowest_ask || null, peak: r?.highest_deal_price || null,
            age: daysSince(r?.recent_deal_absolute?.date, universe.updatedAt),
            gap: change(r?.current_lowest_ask, r?.recent_deal_absolute?.price),
            drop: change(r?.recent_deal_absolute?.price, r?.highest_deal_price),
            askDrop: change(r?.current_lowest_ask, r?.highest_deal_price) };
    });
    const comparable = rows.filter(r => r.gap !== null && r.age !== null && r.age <= 365);
    const mean = (values: (number | null)[]) => { const v = values.filter((n): n is number => n !== null); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null; };
    let series: MacroPoint[] = [];
    try {
        series = JSON.parse(await fs.readFile(path.join(process.cwd(), 'src/data/macro_tx_index.json'), 'utf8'));
    }
    catch { /* Optional historical aggregate. */ }
    const month = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit' }).format(new Date(universe.updatedAt));
    series = series.filter(p => p.month <= month).sort((a, b) => a.month.localeCompare(b.month));
    return { updatedAt: universe.updatedAt, rows, comparable,
        count: rows.length, typeCount: universe.groups.reduce((n, g) => n + g.stats.length, 0),
        coveredTypes: universe.summaries.reduce((n, s) => n + s.availableTypes, 0),
        meanDrop: mean(comparable.map(r => r.drop)), meanGap: mean(comparable.map(r => r.gap)), meanAskDrop: mean(comparable.map(r => r.askDrop)),
        below: comparable.filter(r => (r.gap ?? 0) < 0).length,
        stale: rows.filter(r => r.age === null || r.age > 365).length,
        series: series.slice(-36), latest: series.at(-1) || null,
        lastComplete: series.filter(p => p.month < month).at(-1) || null, month };
});
export type MarketData = Awaited<ReturnType<typeof readMarket>>;
export const complexHref = (r: MarketData['rows'][number]) => `/complex?id=${encodeURIComponent(r.id)}&area=${encodeURIComponent(r.area)}`;
