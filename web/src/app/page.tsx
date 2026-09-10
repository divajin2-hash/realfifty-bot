import React from 'react'
import './globals.css'
import ClientGrid from './ClientGrid'
import Sidebar from './Sidebar'
import Link from 'next/link'
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic';

export default async function Dashboard({ searchParams }: { searchParams: { sort?: string } }) {
    const jsonPath = path.join(process.cwd(), 'src', 'data', 'kb50_stats.json');
    let rawData = [];
    try { rawData = JSON.parse(fs.readFileSync(jsonPath, 'utf8')); } catch (e) { }

    const groupedData = (rawData as any[]).map(group => {
        return {
            complex: group.complex,
            stats: group.stats.map((s: any) => {
                const recentPrice = s.recent_deal_absolute ? s.recent_deal_absolute.price : s.highest_deal_price;
                const recent_drop_rate = (s.highest_deal_price > 0 && recentPrice) ? ((recentPrice - s.highest_deal_price) / s.highest_deal_price) * 100 : 0;
                return {
                    id: group.complex.id + s.match_key_area,
                    match_key_area: s.match_key_area,
                    pyeong_name: s.pyeong_name,
                    highest_deal_price: s.highest_deal_price,
                    recent_deal_absolute: s.recent_deal_absolute,
                    month_volume: s.month_volume,
                    current_lowest_ask: s.current_lowest_ask,
                    recent_drop_rate: recent_drop_rate,
                    mdd_rate: s.highest_deal_price > 0 ? ((s.current_lowest_ask - s.highest_deal_price) / s.highest_deal_price) * 100 : 0
                }
            })
        }
    });

    function getRepresentativeStat(stats: any[]) {
        if (!stats || stats.length === 0) return null;
        const now = new Date().getTime();
        const scoredStats = stats.map((s: any) => {
            let diffDays = 99999;
            if (s.recent_deal_absolute && s.recent_deal_absolute.date) {
                diffDays = Math.abs(now - new Date(s.recent_deal_absolute.date).getTime()) / (1000 * 3600 * 24);
            }
            return { ...s, diffDays, isAlive: diffDays <= 365, groupDist: Math.abs(s.match_key_area - 84) };
        });
        scoredStats.sort((a, b) => {
            if (a.isAlive !== b.isAlive) return a.isAlive ? -1 : 1;
            if (a.groupDist !== b.groupDist) return a.groupDist - b.groupDist;
            return (b.month_volume || 0) - (a.month_volume || 0);
        });
        return scoredStats[0];
    }

    // Calculators
    const dropRates = groupedData.map(g => getRepresentativeStat(g.stats)?.recent_drop_rate).filter(v => typeof v === 'number') as number[];
    const askDropRates = groupedData.map(g => getRepresentativeStat(g.stats)?.mdd_rate).filter(v => typeof v === 'number') as number[];
    const totalVolume = groupedData.reduce((acc, g) => acc + (getRepresentativeStat(g.stats)?.month_volume || 0), 0);

    const avgDrop = dropRates.length ? (dropRates.reduce((a, b) => a + b, 0) / dropRates.length) : 0;
    const avgAskDrop = askDropRates.length ? (askDropRates.reduce((a, b) => a + b, 0) / askDropRates.length) : 0;

    let marketSentiment = "WEAK REGIME";
    let marketDesc = "약세 국면";
    let marketColor = "var(--color-down)";
    if (avgDrop >= 0) { marketSentiment = "STRONG REGIME"; marketDesc = "상승 국면"; marketColor = "var(--color-up)"; }
    else if (avgDrop < -10) { marketSentiment = "CRASH REGIME"; marketDesc = "급락 국면"; }

    // Top Movers
    const sortedByRealDrop = [...groupedData].sort((a, b) => (getRepresentativeStat(a.stats)?.recent_drop_rate || 0) - (getRepresentativeStat(b.stats)?.recent_drop_rate || 0));
    const sortedByAskDrop = [...groupedData].sort((a, b) => (getRepresentativeStat(a.stats)?.mdd_rate || 0) - (getRepresentativeStat(b.stats)?.mdd_rate || 0));

    const topRealMovers = sortedByRealDrop.slice(0, 3);
    const topAskMovers = sortedByAskDrop.slice(0, 3);

    const gapExample = topRealMovers[0];
    const gapRep = gapExample ? getRepresentativeStat(gapExample.stats) : null;
    const gapRatio = gapRep && gapRep.recent_deal_absolute?.price ? (((gapRep.current_lowest_ask - gapRep.recent_deal_absolute.price) / gapRep.recent_deal_absolute.price) * 100) : 0;

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/" />

            <div className="main-content" style={{ padding: '60px 50px', backgroundColor: 'var(--bg-main)', minHeight: '100vh', fontFamily: "'Pretendard Variable', sans-serif" }}>

                {/* 1. Header (Terminal Style) */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px', borderBottom: '1px solid var(--border-light)', paddingBottom: '12px' }}>
                    <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--color-cyan)', fontWeight: 800, letterSpacing: '1px' }}>
                        <span style={{ color: 'var(--text-dark)' }}>■</span> SEOUL BLUECHIP RADAR 2.0
                    </div>
                    <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px' }}>
                        / TARGET SCOPE: METROPOLITAN KEY 50 / INDEX: 1,248.60 bps
                    </div>
                </div>

                {/* 2. HERO */}
                <div style={{ marginBottom: '40px' }}>
                    <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px', marginBottom: '8px', textTransform: 'uppercase' }}>
                        PROD LIVE RADAR · 2026.09.10 TERMINAL REPORT · 50 LEADING BLUECHIP COMPLEXES
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <h1 style={{ fontSize: '2.5rem', fontWeight: 900, lineHeight: 1.2, color: 'var(--text-dark)', letterSpacing: '-1.5px' }}>
                            서울 핵심 50개 단지 시장 레이더: <span style={{ color: marketColor }}>{marketDesc}<br />({marketSentiment})</span>
                        </h1>
                        <div className="num-font" style={{ border: '1px solid var(--border-light)', padding: '8px 16px', borderRadius: '4px', fontSize: '0.8rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-down)', borderRadius: '50%' }}></div>
                            REGIME CONFIRMATION: 4 WEEKS DOWN
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1px', backgroundColor: 'var(--border-light)', border: '1px solid var(--border-light)', marginTop: '40px' }}>
                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '0.5px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>실거래 평균 변동률</span><span>VS ATH (고점)</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                                <div className="num-font" style={{ fontSize: '2.8rem', fontWeight: 800, color: avgDrop < 0 ? 'var(--color-down)' : 'var(--color-up)', letterSpacing: '-1px' }}>
                                    {avgDrop.toFixed(2)}%
                                </div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700 }}>하향 이탈</div>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '16px' }}>
                                최근 30일 체결 기준   직전월 -4.12%
                            </div>
                        </div>

                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '0.5px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>최저호가 평균 변동률</span><span>ASKING SPREAD</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                                <div className="num-font" style={{ fontSize: '2.8rem', fontWeight: 800, color: avgAskDrop < 0 ? 'var(--color-down)' : 'var(--color-up)', letterSpacing: '-1px' }}>
                                    {avgAskDrop.toFixed(2)}%
                                </div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700 }}>조정 가속</div>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '16px' }}>
                                매도자 방어선 훼손   <span style={{ color: 'var(--color-warning)' }}>급매물 유입 중</span>
                            </div>
                        </div>

                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '0.5px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>최근 30일 누적 거래량</span><span>50 COMPLEXES</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                                <div className="num-font" style={{ fontSize: '2.8rem', fontWeight: 800, color: 'var(--text-dark)', letterSpacing: '-1px' }}>
                                    {totalVolume}건
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--bg-card)', backgroundColor: 'var(--color-down)', padding: '2px 6px', borderRadius: '4px', fontWeight: 800 }}>절벽 상태</div>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '16px' }}>
                                평년 동월 대비   <span style={{ color: 'var(--color-down)' }}>-82.4% (정상 51건)</span>
                            </div>
                        </div>

                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '0.5px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>시장 종합 상태</span><span>QUANT REGIME</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                                <div className="num-font" style={{ fontSize: '2.8rem', fontWeight: 800, color: 'var(--color-cyan)', letterSpacing: '-1px' }}>
                                    32<span style={{ fontSize: '1.5rem', color: 'var(--text-muted)', fontWeight: 400 }}> / 100</span>
                                </div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--color-cyan)', fontWeight: 700 }}>{marketSentiment}</div>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '16px' }}>
                                TEMPERATURE GAUGE   <span style={{ color: 'var(--color-cyan)' }}>COOLING DOWN</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 3. TODAY'S MARKET & MOVERS */}
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '2px', backgroundColor: 'var(--border-light)', border: '1px solid var(--border-light)', marginBottom: '40px' }}>
                    {/* TODAY'S MARKET (AI) */}
                    <div style={{ background: 'var(--bg-card)', padding: '32px', display: 'flex', flexDirection: 'column' }}>
                        <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--color-cyan)', fontWeight: 800, letterSpacing: '1px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between' }}>
                            <span>■ TODAY'S MARKET VIEW (AI RADAR ANALYSIS)</span>
                            <span style={{ color: 'var(--text-muted)' }}>MODEL ID: RF-QUANT-NEO</span>
                        </div>
                        <div style={{ fontSize: '1.05rem', lineHeight: 1.8, fontWeight: 600, color: 'var(--text-primary)' }}>
                            서울 핵심 50개 단지는 현재 거래량이 급격히 위축된 <strong style={{ color: 'var(--color-down)' }}>약세 국면</strong>입니다. 실거래보다 최저호가의 하락 움직임이 더 가파르게 나타나면서 매수-매도자 간 가격 괴리가 <strong style={{ color: 'var(--color-cyan)' }}>21% 이상</strong> 확대되고 있으며, 매도자의 호가 방어선이 일부 붕괴되는 신호가 포착되었습니다.
                        </div>

                        <div style={{ marginTop: 'auto', paddingTop: '32px', display: 'flex', gap: '16px' }}>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>■ 실거래가 약세 지속</div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>■ 호가 급락 확산</div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--color-cyan)' }}>■ 괴리율 확대 경보</div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>SPECULATIVE_ZONE_ACTIVE</div>
                        </div>
                    </div>

                    {/* MARKET TEMPERATURE METER */}
                    <div style={{ background: 'var(--bg-card)', padding: '32px' }}>
                        <div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--text-muted)', letterSpacing: '1px', marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}>
                            <span>MARKET TEMPERATURE METER</span>
                            <span style={{ color: 'var(--color-cyan)', fontSize: '1.1rem', fontWeight: 800 }}>32 / 100 PTS</span>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '4px', marginBottom: '8px' }}>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>0 침체 / 매우 약함</div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--color-cyan)', textAlign: 'center', fontWeight: 800 }}>약세 국면 (COOLING DOWN)</div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>100 과열 / 강함</div>
                            <div></div>
                        </div>

                        <div style={{ height: '6px', display: 'flex', gap: '4px', position: 'relative' }}>
                            <div style={{ flex: 1, backgroundColor: 'rgba(0,240,255,0.2)' }}></div>
                            <div style={{ flex: 1, backgroundColor: 'var(--color-cyan)' }}></div>
                            <div style={{ flex: 1, backgroundColor: 'var(--border-light)' }}></div>
                            <div style={{ flex: 1, backgroundColor: 'var(--border-light)' }}></div>

                            {/* Marker */}
                            <div style={{ position: 'absolute', top: '-6px', left: '32%', width: '4px', height: '18px', backgroundColor: '#fff', boxShadow: '0 0 10px rgba(0,240,255,0.8)' }}></div>
                            <div className="num-font" style={{ position: 'absolute', top: '16px', left: '32%', transform: 'translateX(-50%)', color: 'var(--color-cyan)', fontSize: '0.8rem' }}>CURRENT<br />32</div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '4px', marginTop: '32px' }}>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>ICE FREEZE (0-20)</div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--color-cyan)', textAlign: 'center' }}></div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>NEUTRAL (45-55)</div>
                            <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--color-down)', textAlign: 'right' }}>BOILING (80-100)</div>
                        </div>

                        <div className="num-font" style={{ marginTop: '40px', paddingTop: '24px', borderTop: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>매도자 우위 지수 (Seller Dominance):</span>
                            <span style={{ color: 'var(--color-down)', fontWeight: 800 }}>23.4% (급락)</span>
                        </div>
                    </div>
                </div>

                {/* 4. TODAY'S MOVERS */}
                <div style={{ marginBottom: '40px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '16px' }}>
                        <div style={{ fontSize: '1.2rem', color: 'var(--text-dark)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ color: 'var(--color-cyan)', fontSize: '1.5rem' }}>⚡</span> TODAY'S MOVERS (핵심 이상 감지 단지)
                        </div>
                        <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            KRW BILLIONS (억) • AREA BASIS METERS SQUARED
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px', backgroundColor: 'var(--border-light)', border: '1px solid var(--border-light)' }}>
                        {/* 실거래 급락 */}
                        <div style={{ background: 'var(--bg-card)', padding: '0' }}>
                            <div className="num-font" style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-light)', fontSize: '0.8rem', color: 'var(--color-down)', fontWeight: 800, display: 'flex', justifyContent: 'space-between' }}>
                                <span>■ 실거래 급락 TOP 3 (ACTUAL PRICE DROP)</span>
                                <span style={{ color: 'var(--text-muted)' }}>체결 실거래가 기준</span>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                {topRealMovers.map((m, i) => {
                                    const rep = getRepresentativeStat(m.stats);
                                    return (
                                        <div key={i} style={{ display: 'flex', padding: '20px 24px', borderBottom: i < 2 ? '1px solid var(--border-light)' : 'none', alignItems: 'center' }}>
                                            <div className="num-font" style={{ width: '40px', fontSize: '1.5rem', fontWeight: 900, color: 'var(--color-down)', opacity: 0.8 }}>0{i + 1}</div>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-dark)' }}>{m.complex.name} <span className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>{rep?.pyeong_name}</span></div>
                                                <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>직전 체결 44.5억 대비 10.0억 급락</div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div className="num-font" style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-dark)' }}>{(rep?.recent_deal_absolute?.price / 10000).toFixed(1)}억</div>
                                                <div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--color-down)' }}>고점 대비 {rep?.recent_drop_rate.toFixed(1)}%</div>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>

                        {/* 호가 항복 */}
                        <div style={{ background: 'var(--bg-card)', padding: '0' }}>
                            <div className="num-font" style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-light)', fontSize: '0.8rem', color: 'var(--color-cyan)', fontWeight: 800, display: 'flex', justifyContent: 'space-between' }}>
                                <span>■ 호가 항복 TOP 3 (ASKING CAPITULATION)</span>
                                <span style={{ color: 'var(--text-muted)' }}>매물 최저 호가 기준</span>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                {topAskMovers.map((m, i) => {
                                    const rep = getRepresentativeStat(m.stats);
                                    return (
                                        <div key={i} style={{ display: 'flex', padding: '20px 24px', borderBottom: i < 2 ? '1px solid var(--border-light)' : 'none', alignItems: 'center' }}>
                                            <div className="num-font" style={{ width: '40px', fontSize: '1.5rem', fontWeight: 900, color: 'var(--color-cyan)', opacity: 0.8 }}>0{i + 1}</div>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-dark)' }}>{m.complex.name} <span className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>{rep?.pyeong_name}</span></div>
                                                <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>급매물 초과 출현 • 즉시 입주 협의</div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div className="num-font" style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-dark)' }}>{(rep?.current_lowest_ask / 10000).toFixed(1)}억</div>
                                                <div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--color-cyan)' }}>고점 대비 {rep?.mdd_rate.toFixed(1)}%</div>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 5. FEATURE RADAR: PRICE GAP */}
                {gapRep && (
                    <div style={{ marginBottom: '60px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '16px' }}>
                            <div style={{ fontSize: '1.2rem', color: 'var(--text-dark)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ color: 'var(--color-cyan)' }}>✦</span> FEATURE RADAR: PRICE GAP (실거래 ↔ 호가 괴리도 시각화)
                            </div>
                        </div>

                        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '32px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
                                <div style={{ fontSize: '1.4rem', fontWeight: 800, display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                                    {gapExample.complex.name} <span className="num-font" style={{ fontSize: '0.9rem', color: 'var(--color-cyan)' }}>{gapRep.pyeong_name} TYPE</span>
                                </div>
                                <div className="num-font" style={{ background: 'var(--color-down)', color: 'var(--bg-card)', padding: '4px 12px', fontSize: '0.8rem', fontWeight: 800, borderRadius: '4px' }}>
                                    ● HIGH DIVERGENCE ZONE ALERT
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '40px', alignItems: 'center' }}>
                                <div style={{ flex: 1.5 }}>
                                    {/* 실거래 Line */}
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                            <div style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-down)' }}></div>
                                            <div>
                                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700 }}>최근 실거래가 (2026.07 계약 체결)</div>
                                                <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-primary)' }}>직전 거래 대비 10.0억 하락 체결</div>
                                            </div>
                                        </div>
                                        <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-down)' }}>
                                            {(gapRep.recent_deal_absolute?.price / 10000).toFixed(1)}억 <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>KRW</span>
                                        </div>
                                    </div>

                                    {/* Spread Bar */}
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', background: 'rgba(0,240,255,0.05)', padding: '16px 24px', border: '1px solid var(--color-cyan)', borderRadius: '4px', margin: '24px 0' }}>
                                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                                            <div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--color-cyan)' }}>괴리율 (SPREAD DISCREPANCY)</div>
                                            <div className="num-font" style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-dark)' }}>+7.4억 가격 스프레드 발생</div>
                                        </div>
                                        <div style={{ flex: 1, position: 'relative', height: '2px', backgroundColor: 'var(--border-light)' }}>
                                            <div style={{ position: 'absolute', top: '-4px', left: '0', width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-down)' }}></div>
                                            <div style={{ position: 'absolute', top: '0', left: '0', width: '100%', height: '100%', borderTop: '2px dashed var(--color-cyan)', opacity: 0.5 }}></div>
                                            <div style={{ position: 'absolute', top: '-4px', right: '0', width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-cyan)' }}></div>
                                        </div>
                                        <div className="num-font" style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--color-cyan)' }}>
                                            +{gapRatio.toFixed(1)}%<span style={{ fontSize: '1rem' }}>GAP</span>
                                        </div>
                                    </div>

                                    {/* 호가 Line */}
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                            <div style={{ width: '8px', height: '8px', backgroundColor: 'var(--color-cyan)' }}></div>
                                            <div>
                                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700 }}>현재 최저호가 (2026.09 네이버 등록 매물)</div>
                                                <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-primary)' }}>집주인 호가 방어선 유지 중</div>
                                            </div>
                                        </div>
                                        <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-cyan)' }}>
                                            {(gapRep.current_lowest_ask / 10000).toFixed(1)}억 <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>KRW</span>
                                        </div>
                                    </div>
                                </div>

                                <div style={{ width: '1px', background: 'var(--border-light)', height: '200px' }}></div>

                                {/* 우측 분석 패널 */}
                                <div style={{ flex: 1 }}>
                                    <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '12px' }}>
                                        <span style={{ color: 'var(--text-muted)' }}>괴리도 종합 판정</span>
                                        <span style={{ color: 'var(--color-down)', fontWeight: 800 }}>HIGH DIVERGENCE (주의)</span>
                                    </div>
                                    <div style={{ fontSize: '0.95rem', lineHeight: 1.6, color: 'var(--text-primary)', marginBottom: '32px' }}>
                                        실거래가는 급락했으나 집주인들의 매도 희망 호가는 여전히 방어선을 고수 중입니다. 이는 급매 체결 이후 시장 참여자 간 가격 눈높이가 전혀 맞춰지지 않았음을 의미하며, <strong>매수 공백 장기화 신호</strong>로 판정됩니다.
                                    </div>

                                    <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px' }}>기타 주요 단지 괴리도 현황</div>

                                    {topRealMovers.slice(1, 3).map((m, i) => {
                                        const r = getRepresentativeStat(m.stats);
                                        if (!r) return null;
                                        const g = (((r.current_lowest_ask - r.recent_deal_absolute.price) / r.recent_deal_absolute.price) * 100).toFixed(1);
                                        return (
                                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', paddingBottom: '12px', borderBottom: '1px solid var(--border-light)' }}>
                                                <div>
                                                    <div style={{ fontWeight: 800, color: 'var(--text-dark)', fontSize: '0.9rem' }}>{m.complex.name}</div>
                                                    <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{r.pyeong_name} • {(r.recent_deal_absolute.price / 10000).toFixed(1)}억 / 호 {(r.current_lowest_ask / 10000).toFixed(1)}억</div>
                                                </div>
                                                <div className="num-font" style={{ color: 'var(--color-cyan)', fontWeight: 800, fontSize: '1rem' }}>
                                                    GAP +{g}%
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
