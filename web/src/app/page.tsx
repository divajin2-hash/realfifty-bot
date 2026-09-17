import Link from 'next/link';
import AiMarketTalk from './AiMarketTalk';
import TerminalShell, { Metric, Methodology } from './TerminalShell';
import { TrendChart } from './MarketCharts';
import { readMarket, complexHref } from '@/lib/market-data';
import { percent, price } from '@/lib/complex-model';
export const dynamic = 'force-dynamic';
export default async function Today() {
    const d = await readMarket();
    const watch = [...d.comparable].sort((a, b) => (a.gap ?? 0) - (b.gap ?? 0)).slice(0, 5);
    return <TerminalShell active="/" eyebrow="TODAY / MARKET RADAR" title="오늘의 주택시장, 데이터로 읽다" description="실거래와 매도자의 기대 가격을 함께 관찰하는 RealFifty 데일리 레이더" updatedAt={d.updatedAt}>
 <section className="rt-hero"><div className="rf-eyebrow">MARKET SNAPSHOT <span>50개 단지 관측</span></div><h2>같은 시장, 다른 가격.<br />실거래와 호가 사이의 간격을 확인하세요.</h2><p>비교 가능한 {d.comparable.length}개 단지 중 {d.below}곳의 대표 타입 최저호가가 최근 실거래보다 낮습니다. 거래 시점과 타입별 조건을 함께 살펴야 현재 가격의 의미를 읽을 수 있습니다.</p><div className="rt-actions"><Link className="rt-button" href="/market">시장 전체 분석 →</Link><Link className="rt-button secondary" href="/report">데일리 리서치 읽기</Link></div></section>
 <div className="rt-grid four"><Metric label="고점 대비 최근 실거래" value={percent(d.meanDrop)} note={`최근 1년 내 비교 가능 ${d.comparable.length}개 단지 단순 평균`}/><Metric label="평균 호가 괴리" value={percent(d.meanGap)} note="최저호가 ÷ 최근 실거래 − 1"/><Metric label={`${d.latest?.month || '최근 월'} 신고 거래`} value={`${d.latest?.sample_count ?? '—'}건`} note="월 집계 · 진행 중인 월은 잠정치"/><Metric label="실거래 아래 호가" value={`${d.below}/${d.comparable.length}`} note="단지별 대표 타입 기준 · 매수 신호와는 구분"/></div>
 <div className="rt-grid two"><section className="rt-panel"><div className="rt-heading"><h2>실거래의 흐름</h2><span className="rf-badge blue">36개월</span></div><p>월별 실거래 회복률과 신고 거래 수</p><TrendChart data={d.series}/><div className="rt-caption">회복률은 타입별 고점 대비 거래가격 비율의 월 중앙값. 현재 월과 완료 월의 거래량을 동일 기간 증감으로 해석하지 않습니다.</div></section><section className="rt-panel"><div className="rt-heading"><h2>호가 괴리 관찰 목록</h2><Link href="/complex">전체 보기 →</Link></div><p>최근 실거래 대비 호가가 낮은 순서</p>{watch.map(r => <Link className="rt-list-row" key={r.id} href={complexHref(r)}><div><strong>{r.name}</strong><small>{r.areaLabel} · 호가 {price(r.ask)}</small></div><b className="rf-number">{percent(r.gap)}</b></Link>)}</section></div>
 <AiMarketTalk/>
 <div className="rt-grid three"><section className="rt-panel"><div className="rf-eyebrow">01 / COMPLEX</div><h2>가격의 맥락까지</h2><p>타입별 실거래·매물·고점과 거래 공백을 한 화면에서 비교합니다.</p><Link className="rt-download" href="/complex">단지 탐색 →</Link></section><section className="rt-panel"><div className="rf-eyebrow">02 / RESEARCH</div><h2>근거가 남는 리포트</h2><p>핵심 관측, 관심 단지, 해석과 시나리오를 구분하는 리서치 브리핑입니다.</p><Link className="rt-download" href="/report">보고서 열기 →</Link></section><section className="rt-panel"><div className="rf-eyebrow">03 / FACT CHECK</div><h2>기사의 범위부터 검증</h2><p>기사에 나온 지역과 기간의 실거래를 먼저 확인하고, 50개 단지는 보조 자료로 활용합니다.</p><Link className="rt-download" href="/news">기사 검증실 →</Link></section></div><Methodology />
 </TerminalShell>;
}
