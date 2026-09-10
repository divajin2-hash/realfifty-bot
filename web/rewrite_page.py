import sys

new_content = \\
import React from 'react'
import './globals.css'
import ClientGrid from './ClientGrid'
import Sidebar from './Sidebar'
import Link from 'next/link'
import fs from 'fs'
import path from 'path'
import { ArrowDown, ArrowUp, ArrowRight, TrendingDown, Activity, AlertTriangle, AlertCircle } from 'lucide-react'

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

    const sortMethod = (await searchParams)?.sort || 'real_drop_high';
    groupedData.sort((a, b) => {
        const repA = getRepresentativeStat(a.stats);
        const repB = getRepresentativeStat(b.stats);
        const rmA = repA ? repA.recent_drop_rate : 0;
        const rmB = repB ? repB.recent_drop_rate : 0;
        return rmA - rmB; // default ascending (drop high)
    });

    // 1. Calculate Aggregates
    const dropRates = groupedData.map(g => getRepresentativeStat(g.stats)?.recent_drop_rate).filter(v => typeof v === 'number') as number[];
    const askDropRates = groupedData.map(g => getRepresentativeStat(g.stats)?.mdd_rate).filter(v => typeof v === 'number') as number[];
    const totalVolume = groupedData.reduce((acc, g) => acc + (getRepresentativeStat(g.stats)?.month_volume || 0), 0);
    
    const avgDrop = dropRates.length ? (dropRates.reduce((a, b) => a + b, 0) / dropRates.length) : 0;
    const avgAskDrop = askDropRates.length ? (askDropRates.reduce((a, b) => a + b, 0) / askDropRates.length) : 0;

    let marketSentiment = "WEAK";
    let marketDesc = "약세 국면";
    let marketColor = "var(--color-down)";
    if (avgDrop >= 0) { marketSentiment = "STRONG"; marketDesc = "상승 국면"; marketColor = "var(--color-up)"; }
    else if (avgDrop < -10) { marketSentiment = "CRASH"; marketDesc = "급락 국면"; }

    // 2. Extracted Movers (Top 3 drops)
    const sortedByRealDrop = [...groupedData].sort((a,b) => (getRepresentativeStat(a.stats)?.recent_drop_rate||0) - (getRepresentativeStat(b.stats)?.recent_drop_rate||0));
    const sortedByAskDrop = [...groupedData].sort((a,b) => (getRepresentativeStat(a.stats)?.mdd_rate||0) - (getRepresentativeStat(b.stats)?.mdd_rate||0));
    
    const topRealMovers = sortedByRealDrop.slice(0, 3);
    const topAskMovers = sortedByAskDrop.slice(0, 3);

    // 3. Price Gap Example (Asia 선수촌, or #1 Real Drop)
    const gapExample = topRealMovers[0];
    const gapRep = getRepresentativeStat(gapExample?.stats || []);
    const gapRatio = gapRep ? (((gapRep.current_lowest_ask - (gapRep.recent_deal_absolute?.price||0)) / (gapRep.recent_deal_absolute?.price||1)) * 100) : 0;

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/" />
            
            <div className="main-content" style={{ padding: '60px 40px' }}>
                {/* 1. HERO */}
                <div style={{ marginBottom: '60px' }}>
                    <h2 style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '1px', marginBottom: '8px' }}>
                        SEOUL REAL ESTATE MARKET
                    </h2>
                    <h1 style={{ fontSize: '3.5rem', fontWeight: 900, lineHeight: 1.1, color: 'var(--text-dark)', letterSpacing: '-2px' }}>
                        서울 핵심 50개 단지<br />시장 레이더 <span style={{ color: marketColor }}>{marketDesc}</span>
                    </h1>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px', marginTop: '40px' }}>
                        <div style={{ padding: '24px', border: '1px solid var(--border-light)', borderRadius: '12px', background: '#fff' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px' }}>실거래</div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 800, color: avgDrop < 0 ? 'var(--color-down)' : 'var(--color-up)', letterSpacing: '-1px' }}>
                                {avgDrop.toFixed(2)}%
                            </div>
                        </div>
                        <div style={{ padding: '24px', border: '1px solid var(--border-light)', borderRadius: '12px', background: '#fff' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px' }}>최저호가</div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 800, color: avgAskDrop < 0 ? 'var(--color-down)' : 'var(--color-up)', letterSpacing: '-1px' }}>
                                {avgAskDrop.toFixed(2)}%
                            </div>
                        </div>
                        <div style={{ padding: '24px', border: '1px solid var(--border-light)', borderRadius: '12px', background: '#fff' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px' }}>최근 30일 거래</div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-dark)', letterSpacing: '-1px' }}>
                                {totalVolume}건
                            </div>
                        </div>
                        <div style={{ padding: '24px', background: 'var(--text-dark)', borderRadius: '12px', color: '#fff', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                            <div style={{ fontSize: '0.85rem', opacity: 0.8, fontWeight: 700, marginBottom: '8px' }}>시장 상태</div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 900, letterSpacing: '1px' }}>
                                {marketSentiment}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. TODAY'S MARKET & MOVERS */}
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '40px', marginBottom: '80px' }}>
                    {/* TODAY'S MARKET (AI VIEW) */}
                    <div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 800, letterSpacing: '1px', marginBottom: '16px' }}>TODAY'S MARKET</div>
                        <div style={{ fontSize: '1.2rem', lineHeight: 1.6, fontWeight: 600, color: 'var(--text-dark)', padding: '24px', background: '#fff', border: '1px solid var(--border-light)', borderRadius: '16px' }}>
                            <p>서울 핵심 50개 단지는 현재 <strong>거래량이 급격히 위축된 {marketDesc}</strong>입니다.</p>
                            <p style={{ marginTop: '16px' }}>실거래보다 호가의 하락 움직임이 {avgAskDrop < avgDrop ? '더 크게' : '경직되어'} 나타나면서 매수·매도자 간 가격 괴리가 {Math.abs(avgAskDrop - avgDrop) > 2 ? '확대되고' : '유지되고'} 있습니다.</p>
                            <div style={{ marginTop: '32px', borderTop: '1px dashed var(--border-light)', paddingTop: '24px' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '12px' }}>MARKET TEMPERATURE</div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                    <div style={{ flex: 1, height: '6px', background: 'linear-gradient(to right, #E63946, #EAEAEA, #1D3557)', borderRadius: '3px', position: 'relative' }}>
                                        <div style={{ position: 'absolute', top: '50%', left: '32%', transform: 'translate(-50%, -50%)', width: '16px', height: '16px', borderRadius: '50%', background: '#111', border: '3px solid #fff', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }} />
                                    </div>
                                    <div className="num-font" style={{ fontSize: '1.5rem', fontWeight: 800 }}>32</div>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                                    <span>매우 약함</span>
                                    <span>강함</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* TODAY'S MOVERS */}
                    <div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--color-down)', fontWeight: 800, letterSpacing: '1px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <AlertTriangle size={16} /> TODAY'S MOVERS
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                            {/* 급락 */}
                            <div style={{ background: '#fff', border: '1px solid var(--border-heavy)', borderRadius: '16px', padding: '24px' }}>
                                <div style={{ fontSize: '1.1rem', fontWeight: 800, borderBottom: '2px solid var(--border-light)', paddingBottom: '12px', marginBottom: '16px' }}>실거래 급락 (항복)</div>
                                {topRealMovers.map((m, i) => {
                                    const rep = getRepresentativeStat(m.stats);
                                    return (
                                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                            <div style={{ fontWeight: 700 }}>{m.complex.name}</div>
                                            <div className="num-font" style={{ color: 'var(--color-down)', fontWeight: 800, fontSize: '1.1rem' }}>
                                                {rep?.recent_drop_rate.toFixed(1)}%
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                            
                            {/* 호가 하락 */}
                            <div style={{ background: '#fff', border: '1px solid var(--border-light)', borderRadius: '16px', padding: '24px' }}>
                                <div style={{ fontSize: '1.1rem', fontWeight: 800, borderBottom: '2px solid var(--border-light)', paddingBottom: '12px', marginBottom: '16px' }}>호가 급락 (조정)</div>
                                {topAskMovers.map((m, i) => {
                                    const rep = getRepresentativeStat(m.stats);
                                    return (
                                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                            <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{m.complex.name}</div>
                                            <div className="num-font" style={{ color: 'var(--color-down)', fontWeight: 800, fontSize: '1.1rem' }}>
                                                {rep?.mdd_rate.toFixed(1)}%
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 3. PRICE GAP FOCUS */}
                {gapRep && (
                <div style={{ marginBottom: '80px' }}>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 800, letterSpacing: '1px', marginBottom: '16px' }}>PRICE GAP FOCUS</div>
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: '16px', padding: '40px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: '1.6rem', fontWeight: 900, marginBottom: '8px' }}>
                                {gapExample.complex.name} <span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 600 }}>{gapRep.pyeong_name}</span>
                            </div>
                            <div style={{ color: 'var(--text-primary)', fontWeight: 600, lineHeight: 1.5 }}>
                                실거래가 대비 호가가 비정상적으로 높게 형성되어<br/>매수자와 매도자 간의 극심한 가격 줄다리기가 진행 중입니다.
                            </div>
                        </div>
                        
                        <div style={{ flex: 1.5, display: 'flex', alignItems: 'center', gap: '32px' }}>
                            <div style={{ flex: 1, textAlign: 'center', borderRight: '1px solid var(--border-light)' }}>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px' }}>최근 실거래가</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-dark)' }}>
                                    {(gapRep.recent_deal_absolute?.price / 10000).toFixed(1)}억
                                </div>
                            </div>
                            
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                <div style={{ fontSize: '0.75rem', fontWeight: 800, color: gapRatio > 0 ? 'var(--color-warning)' : 'var(--color-up)', background: gapRatio > 0 ? '#FFF4EC' : '#E6F0FF', padding: '4px 12px', borderRadius: '20px', marginBottom: '4px' }}>
                                    시장 괴리도 {gapRatio > 10 ? 'HIGH' : 'LOW'}
                                </div>
                                <ArrowRight size={24} color="var(--border-heavy)" style={{ margin: '8px 0' }}/>
                                <div className="num-font" style={{ fontSize: '1.2rem', fontWeight: 800, color: gapRatio > 0 ? 'var(--color-warning)' : 'var(--color-up)' }}>
                                    {gapRatio > 0 ? '+' : ''}{gapRatio.toFixed(1)}%
                                </div>
                            </div>
                            
                            <div style={{ flex: 1, textAlign: 'center', borderLeft: '1px solid var(--border-light)' }}>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px' }}>현재 최저호가</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-dark)' }}>
                                    {(gapRep.current_lowest_ask / 10000).toFixed(1)}억
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                )}

                {/* 4. LEADING 50 (Original Grid) */}
                <div>
                     <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 800, letterSpacing: '1px', marginBottom: '24px' }}>SEOUL LEADING 50</div>
                     <ClientGrid groupedData={groupedData} />
                </div>
                
            </div>
        </div>
    )
}
\\\
with open("src/app/page.tsx", "w", encoding="utf-8") as f:
    f.write(new_content.replace("\\\","").strip())
print("Rewrite complete")
