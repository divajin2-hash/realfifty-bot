import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import TerminalShell, { Metric, Methodology } from '../TerminalShell';
import { TrendChart } from '../MarketCharts';
import ReportActions from './ReportActions';
import PrintTrendChart from './PrintTrendChart';
import { readReport } from '@/lib/report-data';
import { complexHref } from '@/lib/market-data';
import { percent, price } from '@/lib/complex-model';
export const dynamic = 'force-dynamic';
export default async function ReportPage({ searchParams }: {
    searchParams: Promise<{
        date?: string;
    }>;
}) {
    const r = await readReport((await searchParams).date);
    const d = r.market;
    const report = r.document?.report;
    const watch = [...d.comparable].sort((a, b) => (a.gap ?? 0) - (b.gap ?? 0)).slice(0, 3);
    const evidence: Record<string, string> = { gap: `평균 호가 괴리 ${percent(d.meanGap)}`, drop: `고점 대비 실거래 ${percent(d.meanDrop)}`, below: `실거래 아래 호가 ${d.below}/${d.comparable.length}개`, coverage: `호가 수집 ${d.coveredTypes}/${d.typeCount}타입`, monthly: `${d.latest?.month} 신고 거래 ${d.latest?.sample_count ?? '—'}건 (잠정)`, complete_month: `${d.lastComplete?.month} 신고 거래 ${d.lastComplete?.sample_count ?? '—'}건` };
    return <TerminalShell active="/report" eyebrow="REPORT / RESEARCH DESK" title="데일리 주택시장 리서치" description="핵심 관측에서 검증 가능한 근거와 조건부 시나리오까지" updatedAt={d.updatedAt}>
 {!report && <p className="rt-note">실거래 면적 매칭 기준을 재검토했습니다. 기존 AI 리포트는 재검증 전까지 숨기며, 아래는 수정된 현재 데이터의 계산 결과입니다.</p>}<section className="rt-hero"><div className="rt-report-meta"><span>{r.document ? `RESEARCH / ${r.document.date}` : 'LIVE DATA BRIEF / 현재 스냅샷'}</span><span>{r.document ? 'AI 작성 · 수집 데이터 기반' : '계산 기반 브리핑 · 새 AI 리포트 생성 대기'}</span></div><div className="rf-eyebrow">EXECUTIVE SUMMARY</div><h2>{report?.title || '호가와 실거래의 차이에서, 다음 관측 지점을 찾습니다.'}</h2><p>{report?.summary || `최근 거래가 있는 비교 가능 ${d.comparable.length}개 단지의 대표 타입을 기준으로 가격 위치를 정리했습니다. ${d.below}개 단지에서 최저호가가 최근 체결가보다 낮게 관측됩니다. 호가와 실거래는 다른 물건과 시점의 가격이므로 이를 곧바로 시장 하락이나 매수 기회로 단정하지 않습니다.`}</p></section>
 <div className="rt-grid three"><Metric label="01 / 실거래 가격 위치" value={percent(d.meanDrop)} note={`관측 고점 대비 · ${d.comparable.length}개 단순 평균`}/><Metric label="02 / 호가와 체결가의 간격" value={percent(d.meanGap)} note="현재 최저호가 / 최근 체결가 기준"/><Metric label="03 / 최근 월 신고 거래" value={`${d.latest?.sample_count ?? '—'}건`} note={`${d.latest?.month || '자료 없음'} · 미완결 월, 신고 지연 주의`}/></div>
 {report && <div className="rt-grid three">{report.takeaways.map((s, i) => <section className="rt-panel" key={i}><div className="rf-eyebrow">KEY TAKEAWAY / 0{i + 1}</div><h2>{s.title}</h2><p>{s.body}</p><div className="rt-caption">{s.evidence_ids.map(id => evidence[id] || id).join(' · ')}</div></section>)}</div>}
 <div className="rt-heading"><h2>관찰할 단지</h2><span className="rt-small">대표 타입 호가 괴리가 낮은 순 · 추천 순위 아님</span></div><div className="rt-grid three">{watch.map((s, i) => <section className="rt-panel rt-watch" key={s.id}><div className="rf-eyebrow">WATCH / 0{i + 1}</div><h2><Link href={complexHref(s)}>{s.name} ↗</Link></h2><p>{s.areaLabel}</p><strong className="rf-number">{percent(s.gap)}</strong><dl><dt>최근 실거래</dt><dd>{price(s.trade)}</dd><dt>현재 최저호가</dt><dd>{price(s.ask)}</dd><dt>최근 거래일</dt><dd>{s.tradeDate}</dd></dl></section>)}</div>
 <div className="rt-grid two"><section className="rt-panel"><div className="rf-eyebrow">EVIDENCE / TIME SERIES</div><h2>월별 실거래와 거래 표본</h2><div className="report-screen-chart"><TrendChart data={d.series}/></div><PrintTrendChart data={d.series}/><p className="rt-caption">회복률 = 타입별 관측 고점 대비 거래가격 비율의 월 중앙값. 현재 월은 잠정 집계이며 가격·거래량 표본 구성이 달라질 수 있습니다.</p></section><section className="rt-panel"><div className="rf-eyebrow">EVIDENCE / COVERAGE</div><h2>분석의 범위</h2>{[['선정 단지', `${d.count}개`], ['대표 타입 비교 가능', `${d.comparable.length}개`], ['호가 수집 타입', `${d.coveredTypes}/${d.typeCount}`], ['오래된 거래·거래일 미확인', `${d.stale}개`]].map(([k, v]) => <div className="rt-list-row" key={k}><span>{k}</span><b>{v}</b></div>)}<p className="rt-caption">표본은 RealFifty 선정 단지입니다. 전국·지방 거래 증가나 특정 동의 가격 움직임을 직접 검증하는 모집단이 아닙니다.</p></section></div>
 <section className="rt-panel"><div className="rf-eyebrow">ANALYST COMMENTARY</div><h2>{report ? 'AI 심층 해석' : '해석 프레임 · AI 작성 대기'}</h2>{report ? report.analysis.map((s, i) => <div className="rt-scenario" key={i}><h3>{s.title}</h3><p>{s.body}</p><p className="rt-small">근거: {s.evidence_ids.map(id => evidence[id] || id).join(' · ')}</p></div>) : <><p>호가 괴리는 매도자의 기대 가격과 마지막 체결가의 간격입니다. 거래 후 시간이 오래 지났거나 층·향·상태가 다르면 차이가 커질 수 있습니다. 단지 상세에서 거래일과 매물 조건을 먼저 확인해야 합니다.</p><p>월 신고 건수는 거래 활력을 관찰하는 출발점입니다. 이번 달은 신고가 진행 중이므로 지난달 전체와 직접 비교한 감소율은 제공하지 않습니다. 충분한 신고 기간이 지난 뒤 같은 길이의 기간으로 다시 비교해야 합니다.</p></>}</section>
 <section className="rt-panel"><div className="rf-eyebrow">CONDITIONAL SCENARIOS</div><h2>다음 리포트에서 확인할 조건</h2>{(report?.scenarios || [{ title: '가격 간격이 줄어드는 경우', condition: '같은 타입에서 후속 실거래가 쌓이고 호가와의 차이가 줄어드는지 확인합니다.', implication: '체결을 동반한 가격 수렴인지, 매물 교체에 따른 차이인지 구분합니다.' }, { title: '거래 공백이 이어지는 경우', condition: '완료된 비교 기간에도 거래 표본이 부족한지 확인합니다.', implication: '방향성 판단을 유보하고 단지·타입별 거래 공백을 함께 관찰합니다.' }]).map((s, i) => <div className="rt-scenario" key={i}><h3>{s.title}</h3><p>확인 조건 · {s.condition}</p><p>해석 · {s.implication}</p></div>)}</section>
 {report && <section className="rt-note"><strong>리포트 해석 시 확인하세요</strong><p>선정 단지의 관측 결과이며, 이번 달 거래 건수는 신고가 진행 중인 잠정 수치입니다.</p><details><summary>분석 한계 자세히 보기</summary><ul>{report.limitations.map((limitation, i) => <li key={i}>{limitation}</li>)}</ul></details></section>}<Methodology /><ReportActions date={r.document?.date || ''}/>
 <section className="rt-panel rt-report-archive" style={{ marginTop: 24 }}><h2>리포트 아카이브</h2><p>2026년 9월 16일 발행분부터 제공합니다.</p><form className="rt-controls" action="/report"><label htmlFor="report-date">기록 날짜</label><select name="date" id="report-date" defaultValue={r.date}>{r.dates.map(date => <option key={date}>{date}</option>)}</select><button className="rt-button secondary" type="submit">열기</button></form>{r.legacy && <details><summary className="rt-small">{r.date} 기존 형식 리포트 원문 보기 · 새 검증 기준 적용 전</summary><p className="rt-note" style={{ marginTop: 15 }}>위 브리핑은 현재 데이터이며, 아래 원문은 과거 생성 기록입니다. 기존 원문의 표본·추론 방식은 새 리서치 기준을 충족하지 않을 수 있습니다.</p><div className="rt-prose"><ReactMarkdown remarkPlugins={[remarkGfm]}>{r.legacy.replaceAll('네이버','매물 정보')}</ReactMarkdown></div></details>}{!r.dates.length && <p>아직 생성된 보고서가 없습니다.</p>}</section>
 </TerminalShell>;
}
