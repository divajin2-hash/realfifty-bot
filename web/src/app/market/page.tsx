import MarketInterpretation from '../MarketInterpretation';
import TerminalShell, { Metric, Methodology } from '../TerminalShell';
import { Matrix } from '../MarketCharts';
import { readMarket } from '@/lib/market-data';
import {readMarketExtras} from '@/lib/market-extras';
import {MarketHistory,TypeRankings} from './MarketExtras';
import { percent } from '@/lib/complex-model';
export const dynamic = 'force-dynamic';
export default async function Market() {
    const [d,extras] = await Promise.all([readMarket(),readMarketExtras()]);
    const bands = [{ label: '실거래 아래 호가', count: d.comparable.filter(r => (r.gap ?? 0) < 0).length }, { label: '실거래 대비 0~10% 높은 호가', count: d.comparable.filter(r => (r.gap ?? 0) >= 0 && (r.gap ?? 0) < 10).length }, { label: '실거래 대비 10% 이상 높은 호가', count: d.comparable.filter(r => (r.gap ?? 0) >= 10).length }];
    return <TerminalShell active="/market" eyebrow="MARKET / CROSS-SECTION" title="가격의 방향과 시장의 간격" description="동일한 대표 타입 기준으로 50개 단지의 가격 위치와 거래 흐름을 비교합니다." updatedAt={d.updatedAt}>
 <div className="rt-grid four"><Metric label="평균 호가 괴리" value={percent(d.meanGap)} note={`비교 가능 ${d.comparable.length}개 대표 타입`}/><Metric label="고점 대비 최근 실거래" value={percent(d.meanDrop)} note="기간 수익률이 아닌 관측 고점과의 거리"/><Metric label="직전 완료 월 거래" value={`${d.lastComplete?.sample_count ?? '—'}건`} note={`${d.lastComplete?.month || '미수집'} · 이후 신고로 수정될 수 있음`}/><Metric label="현재 호가 수집 범위" value={`${d.coveredTypes}/${d.typeCount}`} note="타입 기준 · 거래 없는 타입도 포함"/></div>
 <div className="rt-grid two"><section className="rt-panel"><div className="rf-eyebrow">PRICE POSITION</div><h2>가격 괴리 매트릭스</h2><p>같은 낙폭이어도 매도자의 기대 가격은 다릅니다.</p><Matrix rows={d.rows}/></section><section className="rt-panel"><div className="rf-eyebrow">MARKET BREADTH</div><h2>호가의 분포</h2><p>최근 365일 안에 거래된 대표 타입만 비교</p><div className="rt-bars">{bands.map(b => <div key={b.label}><div className="rt-bar-label"><span>{b.label}</span><strong>{b.count}개</strong></div><div className="rt-bar-track"><div className="rt-bar-fill" style={{ width: `${d.comparable.length ? 100 * b.count / d.comparable.length : 0}%` }}/></div></div>)}</div><p className="rt-caption">표본 밖 단지와 거래 없는 타입의 상황은 다를 수 있습니다. 오래된 거래 또는 거래일 미확인 단지 {d.stale}곳은 비교 평균에서 제외합니다.</p></section></div>
 <MarketInterpretation data={d}/>
 <MarketHistory history={extras.history} asks={extras.asks}/><TypeRankings representatives={d.rows} allTypes={extras.rows}/><Methodology />
 </TerminalShell>;
}
