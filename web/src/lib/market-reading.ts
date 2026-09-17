import type { ComplexGroup } from './complex-model';

export function compareVolume(groups: ComplexGroup[], now = new Date()) {
  const stamp = groups[0]?.generated_at;
  if (!stamp || groups.some(g => g.generated_at !== stamp) || !Number.isFinite(Date.parse(stamp))) return null;
  const elapsed = now.getTime() - Date.parse(stamp);
  if (elapsed < 0 || elapsed > 3 * 86400000) return null;
  const local = new Date(Date.parse(stamp) + 9 * 3600000);
  const year = local.getUTCFullYear(), month = local.getUTCMonth();
  const day = Math.min(local.getUTCDate() - 1, new Date(Date.UTC(year, month, 0)).getUTCDate());
  if (day < 1) return null;
  const fmt = (d: Date) => d.toISOString().slice(0, 10);
  const start = fmt(new Date(Date.UTC(year, month, 1)));
  const end = fmt(new Date(Date.UTC(year, month, day)));
  const previousStart = fmt(new Date(Date.UTC(year, month - 1, 1)));
  const previousEnd = fmt(new Date(Date.UTC(year, month - 1, day)));
  let current = 0, previous = 0;
  const seen = new Set<string>();
  for (const group of groups) {
    if (!group.stats.length) return null;
    for (const stat of group.stats) {
      if (!Array.isArray(stat.all_trades_history)) return null;
      for (const trade of stat.all_trades_history) {
        if (!(trade.date >= previousStart && trade.date <= end)) continue;
        // Do not guess whether indistinguishable transactions are duplicates.
        if (!trade.id) return null;
        const key = `${group.complex.id}:${trade.id}`;
        if (seen.has(key)) continue;
        seen.add(key);
        if (trade.date >= start && trade.date <= end) current++;
        if (trade.date >= previousStart && trade.date <= previousEnd) previous++;
      }
    }
  }
  return { stamp, start, end, previousStart, previousEnd, current, previous,
    change: previous ? (current / previous - 1) * 100 : null, complexes: groups.length };
}
