export interface Trade { id?: string; date: string; price: number; floor?: number; type?: string }
export interface Listing { price: number; floor?: string; direction?: string; realtor?: string; desc?: string; date?: string }
export interface AreaStat {
  transaction_match?: {status: 'area_matched'|'shared_area'|'ambiguous'|'unmatched';basis?:string;crosschecked_trade_count?:number;candidate_types:number;reference_trade_count:number;excluded_missing_area:number};
  match_key_area: number; pyeong_name?: string; naver_ptp_no?: string;
  exclusive_area?: number; supply_area?: number;
  highest_deal_price: number; highest_deal_date?: string;
  recent_deal_absolute?: Trade | null; current_lowest_ask: number;
  month_volume?: number; sale_count?: number; jeonse_lowest_ask?: number;
  jeonse_count?: number; all_trades_history?: Trade[]; month_deals?: Trade[];
  top_5_listings?: Listing[];
}
export interface ComplexGroup { generated_at?: string; complex: { id: string; name: string; address: string }; stats: AreaStat[] }
export interface ComplexSummary {
  id: string; name: string; address: string; typeCount: number;
  representative: AreaStat | null; volume: number; availableTypes: number;
}
export interface ComplexDetail extends ComplexGroup {
  chart: Record<string, { trades?: Trade[]; asks?: Trade[]; volume?: { month: string; count: number }[] }>;
  updatedAt: string; reportDate: string | null;
}
export const positive = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value) && value > 0;
export const change = (value: number | undefined | null, base: number | undefined | null): number | null =>
  positive(value) && positive(base) ? (value / base - 1) * 100 : null;
export const price = (value: number | undefined | null, digits = 2) => positive(value)
  ? `${(value / 100000000).toLocaleString('ko-KR', { maximumFractionDigits: digits })}억` : '미수집';
export const percent = (value: number | null) => value === null || !Number.isFinite(value) ? '—' : `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
export const areaKey = (stat: AreaStat) => `${stat.naver_ptp_no || ''}:${stat.pyeong_name || ''}:${stat.exclusive_area || stat.match_key_area}`;
export const areaLabel = (stat: AreaStat) => `전용 ${stat.exclusive_area || stat.match_key_area}㎡`;
export function daysSince(date: string | undefined, asOf: string): number | null {
  if (!date) return null;
  const parsed = new Date(asOf);
  if (!Number.isFinite(parsed.getTime())) return null;
  const kstDate = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit' }).format(parsed);
  const days = Math.floor((Date.parse(kstDate) - Date.parse(date.slice(0, 10))) / 86400000);
  return Number.isFinite(days) && days >= 0 ? days : null;
}
export function representative(stats: AreaStat[], asOf: string): AreaStat | null {
  const candidates = stats.filter(s => positive(s.current_lowest_ask) && positive(s.recent_deal_absolute?.price));
  const usable = candidates.length ? candidates : stats;
  return [...usable].sort((a, b) => {
    const ageA = daysSince(a.recent_deal_absolute?.date, asOf) ?? Infinity;
    const ageB = daysSince(b.recent_deal_absolute?.date, asOf) ?? Infinity;
    return Number(ageA > 365) - Number(ageB > 365)
      || Math.abs((a.exclusive_area || a.match_key_area) - 84) - Math.abs((b.exclusive_area || b.match_key_area) - 84)
      || ageA - ageB;
  })[0] || null;
}
export function signal(stat: AreaStat | null, asOf: string): { label: string; tone: string } {
  if (!stat) return { label: '데이터 없음', tone: 'muted' };
  const gap = change(stat.current_lowest_ask, stat.recent_deal_absolute?.price);
  if (gap === null) return { label: '비교 자료 부족', tone: 'muted' };
  if ((daysSince(stat.recent_deal_absolute?.date, asOf) ?? Infinity) > 365) return { label: '오래된 실거래', tone: 'amber' };
  if (gap >= 10) return { label: '호가 괴리 확대', tone: 'amber' };
  if (gap <= -5) return { label: '실거래 아래 호가', tone: 'blue' };
  return { label: '가격 근접', tone: 'mint' };
}
