'use client';

import SiteFooter from '../SiteFooter';
import SampleScope from '../SampleScope';
import RentalMetrics from './RentalMetrics';
import { useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { Activity, ArrowRight, ArrowUpRight, Building2, Check, ChevronDown, Database, Download, Info, Search, SlidersHorizontal, Sparkles, Star, X } from 'lucide-react';
import { CartesianGrid, ComposedChart, Line, ReferenceLine, ResponsiveContainer, Scatter, Tooltip, XAxis, YAxis } from 'recharts';
import Sidebar from '../Sidebar';
import CommunityPanel from '../CommunityPanel';
import {useMember,memberRequest} from '../MemberProvider';
import useWatchlist from '../useWatchlist';
import {PriceAlert} from '../MemberActions';
import { areaKey, areaLabel, change, daysSince, percent, positive, price, representative, signal, type ComplexDetail, type ComplexSummary } from '@/lib/complex-model';
import './terminal.css';

function localDate(value: string) { return new Date(value).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }); }
function shortDate(value?: string) { return value ? value.replaceAll('-', '.') : '확인 불가'; }
function Signed({ value }: { value: number | null }) { return <span className={`rf-number ${value === null ? 'rf-muted' : value < 0 ? 'rf-blue' : value > 0 ? 'rf-rose' : ''}`}>{percent(value)}</span>; }
function Metric({ label, value, hint, tone = '' }: { label: string; value: string; hint: string; tone?: string }) {
  return <div className="rf-metric"><span>{label}</span><strong className={`rf-number ${tone}`}>{value}</strong><small>{hint}</small></div>;
}

export default function ComplexTerminal({ summaries, initialDetail, updatedAt, initialArea, initialTab }: {
  summaries: ComplexSummary[]; initialDetail: ComplexDetail | null; updatedAt: string; initialArea?: string; initialTab?: string;
}) {
  const [detail, setDetail] = useState(initialDetail);
  const [selectedArea, setSelectedArea] = useState(() => {
    const rep = initialDetail ? representative(initialDetail.stats, updatedAt) : null;
    return initialArea || (rep ? areaKey(rep) : '');
  });
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('gap');
  const [period, setPeriod] = useState(36);
  const [tab, setTab] = useState(initialTab === 'discussion' ? 'discussion' : 'trades');
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [showExplorer, setShowExplorer] = useState(true);
  const request = useRef<AbortController | null>(null);
  const detailRef = useRef<HTMLElement>(null);
  const {requireLogin,ready}=useMember();
  const {watched,error:watchError}=useWatchlist();
  const visible = useMemo(() => summaries.filter(c => {
    if (!`${c.name} ${c.address}`.toLowerCase().includes(query.trim().toLowerCase())) return false;
    if (filter === 'watch') return watched.includes(c.id);
    if (filter === 'gap') return (change(c.representative?.current_lowest_ask, c.representative?.recent_deal_absolute?.price) ?? -Infinity) >= 10;
    if (filter === 'below') return (change(c.representative?.current_lowest_ask, c.representative?.recent_deal_absolute?.price) ?? Infinity) < 0;
    return true;
  }).sort((a, b) => {
    if (sort === 'name') return a.name.localeCompare(b.name, 'ko');
    if (sort === 'volume') return b.volume - a.volume;
    if (sort === 'price') return (a.representative?.current_lowest_ask || Infinity) - (b.representative?.current_lowest_ask || Infinity);
    return (change(b.representative?.current_lowest_ask, b.representative?.recent_deal_absolute?.price) ?? -Infinity) - (change(a.representative?.current_lowest_ask, a.representative?.recent_deal_absolute?.price) ?? -Infinity);
  }), [summaries, query, filter, sort, watched]);
  const stats = useMemo(() => [...(detail?.stats || [])].sort((a, b) => (a.exclusive_area || a.match_key_area) - (b.exclusive_area || b.match_key_area) || areaKey(a).localeCompare(areaKey(b))), [detail]);
  const active = stats.find(s => areaKey(s) === selectedArea) || representative(stats, updatedAt);
  const recent = active?.recent_deal_absolute;
  const gap = change(active?.current_lowest_ask, recent?.price);
  const drop = change(recent?.price, active?.highest_deal_price);
  const age = daysSince(recent?.date, detail?.updatedAt || updatedAt);
  const status = signal(active, detail?.updatedAt || updatedAt);
  const history = (() => {
    const chart = detail?.chart[active?.pyeong_name || ''];
    const trades = [...(active?.all_trades_history || [])].filter(t => positive(t.price)).sort((a, b) => a.date.localeCompare(b.date));
    const asks = [...(chart?.asks || [])].filter(t => positive(t.price)).sort((a, b) => a.date.localeCompare(b.date));
    return { trades, asks };
  })();
  const chartData = (() => {
    const end = new Date(updatedAt);
    const start = new Date(end); start.setUTCMonth(start.getUTCMonth() - period);
    const cutoff = period === 0 ? 0 : start.getTime();
    return [
      ...history.trades.map(t => ({ time: Date.parse(t.date), deal: t.price / 100000000, ask: null as number | null })),
      ...history.asks.map(t => ({ time: Date.parse(t.date), ask: t.price / 100000000, deal: null as number | null })),
    ].filter(t => Number.isFinite(t.time) && t.time >= cutoff).sort((a, b) => a.time - b.time);
  })();
  const listings = [...(active?.top_5_listings || [])].filter(l => positive(l.price)).sort((a, b) => a.price - b.price);
  const typeCount = summaries.reduce((n, s) => n + s.typeCount, 0);
  const coverage = summaries.reduce((n, s) => n + s.availableTypes, 0);

  async function selectComplex(id: string) {
    if (id === detail?.complex.id) { request.current?.abort(); setPending(null); detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
    request.current?.abort();
    const controller = new AbortController(); request.current = controller;
    setPending(id); setError('');
    try {
      const response = await fetch(`/api/complexes/${encodeURIComponent(id)}`, { signal: controller.signal });
      if (!response.ok) throw new Error('load');
      const next: ComplexDetail = await response.json();
      if (controller.signal.aborted) return;
      const rep = representative(next.stats, next.updatedAt);
      const key = rep ? areaKey(rep) : '';
      setDetail(next); setSelectedArea(key); setTab('trades'); setPending(null);
      window.history.replaceState(null, '', `/complex?id=${encodeURIComponent(id)}&area=${encodeURIComponent(key)}`);
      detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch {
      if (!controller.signal.aborted) { setError('단지 데이터를 불러오지 못했습니다. 단지를 다시 선택해 주세요.'); setPending(null); }
    }
  }
  function chooseArea(key: string) {
    setSelectedArea(key);
    if (detail) window.history.replaceState(null, '', `/complex?id=${encodeURIComponent(detail.complex.id)}&area=${encodeURIComponent(key)}`);
  }
  async function toggleWatch() {
    if (!detail || !requireLogin('관심 단지를 여러 기기에서 보려면 로그인하세요.')) return;
    try { await memberRequest('watch',{complex_id:detail.complex.id,enabled:!watched.includes(detail.complex.id)});window.dispatchEvent(new Event('rf-watchlist'));setNotice('계정의 관심 단지를 변경했습니다.'); }
    catch(e){setNotice((e as Error).message);}
  }
  function exportTrades() {
    if (!detail || !active) return;
    const rows = [['계약일', '거래금액(원)', '전용면적(㎡)', '타입'], ...history.trades.map(t => [t.date, t.price, active.exclusive_area || active.match_key_area, active.pyeong_name || ''])];
    const csv = '\uFEFF' + rows.map(r => r.map(v => `"${String(v).replaceAll('"', '""')}"`).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const a = document.createElement('a'); a.href = url; a.download = `RealFifty_${detail.complex.name}_${active.pyeong_name || '평형'}_실거래.csv`; a.click(); URL.revokeObjectURL(url);
    setNotice('선택 평형의 실거래 이력을 내보냈습니다.');
  }

  return <div className="app-wrapper rf-app">
    <Sidebar activePath="/complex" />
    <main className="rf-workspace">
      <header className="rf-topbar"><div><span className="rf-kicker">REALFIFTY INTELLIGENCE</span><span className="rf-top-divider">/</span><span>단지 분석</span></div><div className="rf-source"><span className="rf-status-dot" /> 로컬 스냅샷 <span className="rf-number">{localDate(updatedAt)} KST</span></div></header>
      <section className="rf-page-heading"><div><div className="rf-eyebrow">COMPLEX EXPLORER <span>01 — 50</span></div><h1>숫자 너머, 단지의 흐름을 읽다.</h1><p>대한민국 대표 50개 아파트의 실거래와 호가를 같은 평형에서 비교합니다.</p></div><Link href="/market" className="rf-text-link">시장 전체 보기 <ArrowUpRight size={16} /></Link></section>
      <section className="rf-universe" aria-label="분석 데이터 범위"><div><Building2 size={18} /><span>분석 대상</span><strong>{summaries.length}<small>개 단지</small></strong></div><div><SlidersHorizontal size={18} /><span>등록 평형</span><strong>{typeCount}<small>개 타입</small></strong></div><div><Database size={18} /><span>호가 확보</span><strong>{coverage}<small>/ {typeCount} 타입</small></strong></div><div className="rf-universe-note"><Info size={15} /><span>국토부 실거래 · 매물 호가<br />가격은 억원, 면적은 전용 기준</span></div></section>
      <div className="rf-terminal-layout">
        <aside className="rf-explorer" aria-label="단지 탐색">
          <div className="rf-explorer-title"><h2>단지 탐색 <span className="rf-number">{visible.length}</span></h2><button className="rf-icon-button rf-collapse" aria-label={showExplorer ? '단지 목록 접기' : '단지 목록 펼치기'} onClick={() => setShowExplorer(!showExplorer)}><ChevronDown size={18} /></button></div>
          <label className="rf-search"><Search size={17} /><input aria-label="단지명 또는 지역 검색" placeholder="단지명 또는 지역 검색" value={query} onChange={e => { setQuery(e.target.value); setShowExplorer(true); }} />{query && <button onClick={() => setQuery('')} aria-label="검색어 지우기"><X size={15} /></button>}</label>
          <div className="rf-filter-tabs" aria-label="단지 필터">{[['all', '전체'], ['watch', `관심 ${watched.length}`], ['gap', '괴리 10%+'], ['below', '호가 하회']].map(([key, name]) => <button key={key} aria-pressed={filter === key} className={filter === key ? 'active' : ''} onClick={() => { setFilter(key); setShowExplorer(true); }}>{name}</button>)}</div>
          <div className="rf-sort"><span>대표 평형 기준</span><select aria-label="단지 정렬" value={sort} onChange={e => setSort(e.target.value)}><option value="gap">괴리율 높은 순</option><option value="name">단지명 순</option><option value="price">호가 낮은 순</option><option value="volume">거래량 많은 순</option></select></div>
          {showExplorer && <div className="rf-complex-list">{visible.map((c, i) => { const s = c.representative; const status = signal(s, updatedAt); return <button key={c.id} className={`rf-complex-item ${c.id === detail?.complex.id ? 'selected' : ''}`} aria-pressed={c.id === detail?.complex.id} onClick={() => selectComplex(c.id)}>
            <div className="rf-item-top"><span className="rf-rank rf-number">{String(i + 1).padStart(2, '0')}</span><strong>{c.name}</strong>{watched.includes(c.id) && <Star size={13} fill="currentColor" />}</div>
            <div className="rf-item-address">{c.address} · {s ? areaLabel(s) : '평형 없음'}</div><div className="rf-item-prices"><span>실 <b>{price(s?.recent_deal_absolute?.price, 1)}</b></span><span>호 <b>{price(s?.current_lowest_ask, 1)}</b></span></div>
            <div className="rf-item-bottom"><span className={`rf-badge ${status.tone}`}>{pending === c.id ? '불러오는 중…' : status.label}</span><Signed value={change(s?.current_lowest_ask, s?.recent_deal_absolute?.price)} /></div>
          </button>; })}{visible.length === 0 && <div className="rf-empty"><Search size={24} /><strong>{filter === 'watch' ? '저장한 관심 단지가 없습니다.' : '조건에 맞는 단지가 없습니다.'}</strong><p>{filter === 'watch' ? '단지 상세에서 별표를 눌러 저장하세요.' : '단지명이나 필터를 바꿔 보세요.'}</p><button onClick={() => { setQuery(''); setFilter('all'); }}>전체 단지 보기</button></div>}</div>}
          <details className="rf-method"><summary>대표 평형은 어떻게 고르나요?</summary><p>실거래와 호가가 모두 있는 타입 중 최근 1년 거래 여부, 전용 84㎡와의 거리, 최근 거래일 순으로 선택합니다. 단지 전체를 대표하는 확정 시세는 아닙니다.</p></details>
        </aside>
        <section className="rf-analysis" ref={detailRef} aria-label="선택 단지 분석" aria-busy={!!pending}>
          {error && <div className="rf-error" role="alert">{error}</div>}
          {notice && <div className="rf-notice" role="status"><Check size={16} />{notice}<button aria-label="알림 닫기" onClick={() => setNotice('')}><X size={15} /></button></div>}
          {!detail || !active ? <div className="rf-empty">분석할 평형 데이터가 없습니다.</div> : <>
            <section className="rf-asset-header">
              <div className="rf-asset-kicker"><span><Building2 size={14} /> COMPLEX INTELLIGENCE</span><span className={`rf-badge ${status.tone}`}>{status.label}</span></div>
              <div className="rf-asset-title"><div><h2>{detail.complex.name}</h2><p>{detail.complex.address}<span>·</span>{stats.length}개 평형 데이터</p></div><button className={`rf-watch ${watched.includes(detail.complex.id) ? 'saved' : ''}`} disabled={!ready} onClick={toggleWatch} aria-pressed={watched.includes(detail.complex.id)}><Star size={17} fill={watched.includes(detail.complex.id) ? 'currentColor' : 'none'} />{watched.includes(detail.complex.id) ? '관심 단지' : '관심 저장'}</button></div>
              {active&&<PriceAlert complexId={detail.complex.id} area={areaKey(active)}/>}
              {watchError&&<p role="status">{watchError}</p>}
              <div className="rf-area-select"><label htmlFor="rf-area">분석 평형</label><select id="rf-area" value={areaKey(active)} onChange={e => chooseArea(e.target.value)}>{stats.map(s => <option value={areaKey(s)} key={areaKey(s)}>{s.pyeong_name || '타입 미상'} · {areaLabel(s)}{!positive(s.current_lowest_ask) ? ' · 호가 미수집' : ''}</option>)}</select><span>공급 {active.supply_area ? `${active.supply_area}㎡ · ${(active.supply_area / 3.3058).toFixed(1)}평` : '미확인'}</span></div>
              <div className="rt-note"><strong>실거래 연결 기준</strong><p>{active.transaction_match?.status === 'shared_area' ? `동일 전용면적 ${active.transaction_match.candidate_types}개 타입의 공통 실거래입니다. 세부 타입은 구분되지 않으며, 선택 타입의 호가와 공통 거래를 비교합니다.` : active.transaction_match?.status === 'area_matched' ? '전용면적이 일치하는 거래와 계약일·금액·층·거래 종류 대조로 확인된 거래를 연결했습니다. 평면 타입 코드가 직접 확인된 것은 아닙니다.' : '원본 전용면적으로 연결 가능한 거래가 없습니다. 정수 면적만 있는 거래와 근접 면적 거래는 임의로 배정하지 않습니다.'}</p>{!!active.transaction_match?.crosschecked_trade_count && <p>면적 표기 차이가 있지만 거래 대조로 확인된 {active.transaction_match.crosschecked_trade_count}건을 포함합니다. 다른 근접 면적 거래까지 확대 적용하지 않습니다.</p>}<p>2014년 이후 국토부 일반 매매와 분양권·입주권 이력을 포함하며, 취소 거래와 직거래는 제외합니다. 준공 전 권리 거래도 포함되며, 거래 구분은 아래 원장에서 확인하세요. 고점·가격 차이는 권리와 거래 조건이 다른 기록 간 비교일 수 있습니다.</p></div><RentalMetrics stat={active}/><div className="rf-metrics"><Metric label="최근 실거래" value={price(recent?.price)} hint={`${shortDate(recent?.date)}${recent?.floor != null ? ` · ${recent.floor}층` : ''}`} /><Metric label="현재 최저호가" value={price(active.current_lowest_ask)} hint={!positive(active.current_lowest_ask) ? '현재 호가 없음 · 과거 이력 별도' : history.asks.at(-1)?.date ? `${shortDate(history.asks.at(-1)?.date)} 수집 이력` : '수집일 확인 필요'} tone="rf-mint" /><Metric label="고점 대비 실거래" value={percent(drop)} hint={`고점 ${price(active.highest_deal_price)} · ${shortDate(active.highest_deal_date)}`} tone={drop !== null && drop < 0 ? 'rf-blue' : ''} /><Metric label="실거래 ↔ 호가 괴리" value={percent(gap)} hint={gap === null ? '비교 가능한 가격이 필요합니다' : `호가가 실거래보다 ${gap >= 0 ? '높음' : '낮음'}`} tone={gap !== null && gap >= 10 ? 'rf-amber' : ''} /></div>
            </section>
            <div className="rf-detail-grid"><div className="rf-detail-main">
              <section className="rf-panel rf-chart-panel"><div className="rf-panel-heading"><div><span className="rf-eyebrow">PRICE HISTORY</span><h3>가격의 흐름과 두 시장의 거리</h3></div><div className="rf-segment" aria-label="차트 기간">{[[12, '1년'], [36, '3년'], [0, '전체']].map(([value, label]) => <button key={value} className={period === value ? 'active' : ''} aria-pressed={period === value} onClick={() => setPeriod(Number(value))}>{label}</button>)}</div></div><div className="rf-chart-legend"><span><i className="deal" />실거래</span><span><i className="ask" />최저호가</span><span className="rf-chart-unit">단위: 억원</span></div>
                <div className="rf-chart">{chartData.length ? <ResponsiveContainer width="100%" height="100%"><ComposedChart data={chartData} margin={{ top: 15, right: 15, bottom: 0, left: -20 }}><CartesianGrid stroke="#26313c" strokeDasharray="3 6" vertical={false} /><XAxis dataKey="time" type="number" domain={['dataMin', 'dataMax']} scale="time" tickFormatter={v => new Date(v).toISOString().slice(2, 7).replace('-', '.')} stroke="#85909f" fontSize={11} minTickGap={40} tickLine={false} axisLine={false} /><YAxis domain={['auto', 'auto']} stroke="#85909f" fontSize={11} tickLine={false} axisLine={false} /><Tooltip labelFormatter={v => shortDate(new Date(Number(v)).toISOString().slice(0, 10))} formatter={(v, _name, item) => item.dataKey === 'time' ? null : `${Number(v).toFixed(2)}억`} contentStyle={{ background: '#17212d', border: '1px solid #334455', borderRadius: 8, color: '#e8edf4' }} />{positive(active.highest_deal_price) && <ReferenceLine y={active.highest_deal_price / 100000000} stroke="#566273" strokeDasharray="4 4" />}<Line dataKey="ask" name="최저호가" stroke="#66d9bc" strokeWidth={2} dot={false} connectNulls isAnimationActive={false} /><Scatter dataKey="deal" name="실거래" fill="#79afff" isAnimationActive={false} /></ComposedChart></ResponsiveContainer> : <div className="rf-empty">선택한 기간에 수집된 가격 이력이 없습니다.</div>}</div>
                <div className="rf-chart-caption"><span>● 점: 실제 계약 · 선: 수집된 호가 · 점선: 역대 최고 실거래</span><span>{history.asks.length ? `호가 이력 ${history.asks[0].date}부터` : '호가 이력 미수집'}</span></div>
              </section>
              <section className="rf-panel rf-evidence"><div className="rf-evidence-header"><div className="rf-tabs" aria-label="근거 데이터">{[['trades', '실거래 원장'], ['listings', '최저호가 매물'], ['types', '평형 비교'], ['discussion', '토론']].map(([key, label]) => <button key={key} className={tab === key ? 'active' : ''} aria-pressed={tab === key} onClick={() => setTab(key)}>{label}</button>)}</div><button className="rf-icon-button" aria-label="실거래 CSV 다운로드" title="선택 평형의 전체 실거래 CSV" onClick={exportTrades} disabled={!history.trades.length}><Download size={17} /></button></div>
                {tab === 'discussion' && <CommunityPanel key={detail.complex.id} complexId={detail.complex.id} complexName={detail.complex.name} area={areaKey(active)} areaLabel={areaLabel(active)} trade={recent?.price} ask={active.current_lowest_ask}/>}
                {tab === 'trades' && <><div className="rf-table-scroll"><table><caption className="rf-sr-only">선택 평형 최근 실거래 8건</caption><thead><tr><th>계약일</th><th>실거래가</th><th>고점 대비</th><th>층</th><th>거래 구분</th></tr></thead><tbody>{history.trades.slice(-8).reverse().map((t, i) => <tr key={`${t.date}-${i}`}><td className="rf-number">{shortDate(t.date)}</td><td className="rf-number rf-bright">{price(t.price)}</td><td><Signed value={change(t.price, active.highest_deal_price)} /></td><td>{t.floor ?? (t.date === recent?.date && t.price === recent.price ? recent.floor : null) ?? '—'}</td><td>{t.type || '구분 미확인'}</td></tr>)}</tbody></table></div>{!history.trades.length && <div className="rf-empty">선택 타입에 연결 가능한 실거래 이력이 없습니다.</div>}<p className="rf-footnote">최근 8건 · 전체 {history.trades.length}건은 CSV로 확인할 수 있습니다. 층 정보가 없는 과거 거래는 —로 표시합니다. 분양권·입주권 거래는 일반 매매와 권리·가격 조건이 다릅니다.</p></>}
                {tab === 'listings' && <div className="rf-listings">{listings.map((l, i) => <article key={`${l.price}-${i}`}><div><span className="rf-rank rf-number">{String(i + 1).padStart(2, '0')}</span><strong className="rf-number">{price(l.price)}</strong><span className="rf-muted">{l.floor || '층 미확인'} · {l.direction || '방향 미확인'}</span></div><p>{l.desc || '매물 설명 없음'}</p><small>{l.realtor || '중개사 미확인'} · {l.date ? shortDate(l.date) : '등록일 미확인'}</small></article>)}{!listings.length && <div className="rf-empty">이 평형의 개별 매물 정보가 수집되지 않았습니다.</div>}<p className="rf-footnote">수집된 매물 {listings.length}건을 가격순으로 표시합니다. 동·층·수리 상태가 다른 매물이며 중복 등록 여부는 확인이 필요합니다.</p></div>}
                {tab === 'types' && <div className="rf-table-scroll"><table><caption className="rf-sr-only">전체 평형 가격 비교</caption><thead><tr><th>타입 / 전용면적</th><th>실거래</th><th>최저호가</th><th>괴리율</th></tr></thead><tbody>{stats.map(s => <tr key={areaKey(s)} className={areaKey(s) === areaKey(active) ? 'active-row' : ''}><td><button className="rf-type-button" onClick={() => chooseArea(areaKey(s))}>{s.pyeong_name || '타입 미상'}<small>{areaLabel(s)}</small></button></td><td className="rf-number">{price(s.recent_deal_absolute?.price)}</td><td className="rf-number">{price(s.current_lowest_ask)}</td><td><Signed value={change(s.current_lowest_ask, s.recent_deal_absolute?.price)} /></td></tr>)}</tbody></table></div>}
              </section>
            </div><aside className="rf-insights" aria-label="분석 해석 및 데이터 품질">
              <section className="rf-panel rf-reading"><div className="rf-eyebrow"><Activity size={15} /> SIGNAL READING</div><h3>{gap === null ? '비교할 가격이 부족합니다' : gap >= 10 ? '같은 평형, 다른 가격 눈높이' : gap < 0 ? '호가가 최근 실거래 아래에 있습니다' : '실거래와 호가가 가까운 구간'}</h3><p>{gap === null ? '실거래 또는 최저호가가 없어 괴리율을 계산하지 않습니다.' : `최저호가는 최근 실거래보다 ${Math.abs(gap).toFixed(1)}% ${gap >= 0 ? '높습니다' : '낮습니다'}. 거래 시점과 매물 조건을 함께 확인하세요.`}</p><div className="rf-spread"><div><span>최근 실거래</span><b>{price(recent?.price)}</b></div><div className="rf-spread-line"><i /><span>{gap === null ? '비교 불가' : `${Math.abs(((active.current_lowest_ask || 0) - (recent?.price || 0)) / 100000000).toFixed(2)}억 차이`}</span><i /></div><div><span>최저호가</span><b>{price(active.current_lowest_ask)}</b></div></div><small className="rf-rule-label">산식 기반 요약 · AI 예측 아님</small></section>
              <section className="rf-panel rf-liquidity"><div className="rf-eyebrow">TRANSACTION PULSE</div><div className="rf-days"><strong className="rf-number">{age ?? '—'}</strong><span>일</span></div><h3>마지막 계약 이후</h3><p>{shortDate(recent?.date)} 기준</p><div className="rf-mini-stat"><span>선택 평형 최근 30일</span><b>{active.month_volume ?? '—'}건</b></div><p className="rf-footnote">등록 데이터 기준입니다. 신고 지연·취소 반영 시 거래 건수와 공백 기간이 달라질 수 있습니다.</p></section>
              <section className="rf-panel rf-ai"><div className="rf-eyebrow"><Sparkles size={15} /> AI RESEARCH</div><h3>단지에서 시장으로</h3><p>가격 괴리의 배경을 일간 AI 시장 브리핑에서 함께 살펴보세요.</p>{detail.reportDate ? <Link href={`/report?date=${detail.reportDate}`}>AI 시장 리포트 <ArrowRight size={16} /><small>{detail.reportDate} 발간 · 시장 전체 분석</small></Link> : <p>발간된 AI 리포트가 없습니다.</p>}<small className="rf-rule-label">이 단지에 대한 개별 AI 진단은 아직 연결되지 않았습니다.</small></section>
              <section className="rf-quality"><h3><Database size={14} /> 데이터 확인</h3><div><span>실거래</span><b>{active.transaction_match?.status === 'shared_area' ? '동일 면적 공통' : positive(recent?.price) ? '면적 기준 연결' : '연결 자료 없음'}</b></div><div><span>최저호가</span><b>{positive(active.current_lowest_ask) ? '확보' : '미수집'}</b></div><div><span>호가 시계열</span><b>{history.asks.length}개 관측</b></div><div><span>전세 최저호가</span><b>{active.jeonse_count === 0 ? '매물 없음' : price(active.jeonse_lowest_ask)}</b></div>{age !== null && age > 90 && <p className="rf-quality-warning">실거래가 {age}일 전 자료입니다. 현재 호가와 비교할 때 시차를 고려하세요.</p>}<p>갱신: {localDate(detail.updatedAt)} KST<br />로컬 파일 갱신 시각이며 원천 수집 시각과 다를 수 있습니다.</p></section>
            </aside></div>
            <details className="rf-method rf-method-wide"><summary><Info size={14} /> 지표 산식과 데이터 범위</summary><div><p>괴리율 = (현재 최저호가 ÷ 최근 실거래 − 1) × 100. 고점 대비 = (최근 실거래 ÷ 해당 평형 역대 최고 실거래 − 1) × 100. 가격은 원 단위 원본을 1억으로 나누어 표시합니다.</p><p>단지 목록은 대표 평형, 상세는 선택 평형 기준입니다. 동일 평형에도 층·향·동·거래조건 차이가 있으므로 괴리율만으로 저평가나 매수 시점을 확정할 수 없습니다. 호가가 없는 값은 0원으로 해석하지 않습니다.</p><p>평형 매칭은 현재 데이터의 타입 식별자를 따릅니다. 정확한 A/B 타입 매칭 여부와 거래 취소 상태는 원천 검증이 필요합니다. 대한민국 대표 50개 단지 표본이며 전국 주택 전체를 대표하는 공식 지수는 아닙니다.</p></div></details>
          </>}
        </section>
      </div><SampleScope/><SiteFooter/>
    </main>
  </div>;
}
