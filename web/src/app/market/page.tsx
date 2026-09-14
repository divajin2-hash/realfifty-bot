"use client";

import React, { useMemo } from 'react';
import '../globals.css';
import Sidebar from '../Sidebar';
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ScatterChart,
    Scatter, Cell,
    ZAxis,
    BarChart,
    Bar,
    ReferenceLine
} from 'recharts';

import rawData from '@/data/kb50_stats.json';
import macroIndex from '@/data/macro_index.json';
import macroTxIndex from '@/data/macro_tx_index.json';

export default function MarketDashboard() {
    
    // ----------------------------------------------------
    // 1. DATA PREPARATION: Macro Index (Top Line Chart)
    // ----------------------------------------------------
    const indexData = useMemo(() => {
        return macroIndex.map((d: any) => ({
            date: d.date,
            recovery: d.market_recovery_index
        })).slice(-100); // trailing 100 days
    }, []);
    
    const latestRecovery = indexData.length > 0 ? indexData[indexData.length - 1].recovery : 0;
    
    // ----------------------------------------------------
    // 2. DATA PREPARATION: Historical Volume (Bottom Right Bar)
    // ----------------------------------------------------
    const volumeData = useMemo(() => {
        return macroTxIndex.map((d: any) => ({
            month: d.month,
            volume: d.sample_count
        })).slice(-36); // trailing 36 months
    }, []);
    
    const latestVolume = volumeData.length > 0 ? volumeData[volumeData.length - 1].volume : 0;

    // ----------------------------------------------------
    // 3. DATA PREPARATION: Quadrant Scatter & Gauge
    // ----------------------------------------------------
    function getRepresentativeStat(stats: any[]) {
        if (!stats || stats.length === 0) return null;
        const now = new Date().getTime();
        const scoredStats = stats.map((s: any) => {
            let diffDays = 99999;
            if (s.recent_deal_absolute && s.recent_deal_absolute.date) {
                diffDays = Math.abs(now - new Date(s.recent_deal_absolute.date).getTime()) / (1000 * 3600 * 24);
            }
            const hasAsk = s.current_lowest_ask > 0;
            return { ...s, diffDays, isAlive: diffDays <= 365, hasAsk, groupDist: Math.abs(s.match_key_area - 84) };
        });
        
        let validStats = scoredStats.filter(s => s.hasAsk);
        if (validStats.length === 0) validStats = scoredStats;
        
        validStats.sort((a, b) => {
            if (a.isAlive !== b.isAlive) return a.isAlive ? -1 : 1;
            if (a.groupDist !== b.groupDist) return a.groupDist - b.groupDist;
            return (b.month_volume || 0) - (a.month_volume || 0);
        });
        return validStats[0];
    }
    
    const { scatterData, regionStats } = useMemo(() => {
        const scatter: any[] = [];
        const regions = {
            gangnam: { sum: 0, count: 0 },
            mayong: { sum: 0, count: 0 },
            others: { sum: 0, count: 0 }
        };
        
        rawData.forEach((group: any) => {
            const stat = getRepresentativeStat(group.stats);
            if (!stat) return;
            
            const highest = stat.highest_deal_price;
            const recent = stat.recent_deal_absolute?.price;
            const ask = stat.current_lowest_ask;
            
            if (highest > 0 && recent > 0 && ask > 0) {
                const mdd = ((recent - highest) / highest) * 100; // X: 최고가 대비 실거래가 하락률 (MDD)
                const gap = ((ask - recent) / recent) * 100;      // Y: 실거래 ↔ 호가 괴리율
                
                let fill = "#38BDF8";
                if (mdd >= -15 && gap >= 0) fill = "#38BDF8"; // Q1
                else if (mdd >= -15 && gap < 0) fill = "#9CA3AF"; // Q2
                else if (mdd < -15 && gap < 0) fill = "#F87171"; // Q3
                else fill = "#EAB308"; // Q4

                scatter.push({
                    name: group.complex.name,
                    mdd: Number(mdd.toFixed(1)),
                    gap: Number(gap.toFixed(1)),
                    highestStr: (highest / 100000000).toFixed(1) + '억',
                    recentStr: (recent / 100000000).toFixed(1) + '억',
                    askStr: (ask / 100000000).toFixed(1) + '억',
                    fill
                });
                
                // Region calculation
                const rec_rate = (recent / highest) * 100;
                const addr = group.complex.address || "";
                if (addr.includes("강남구") || addr.includes("서초구") || addr.includes("송파구")) {
                    regions.gangnam.sum += rec_rate;
                    regions.gangnam.count++;
                } else if (addr.includes("마포구") || addr.includes("용산구") || addr.includes("성동구")) {
                    regions.mayong.sum += rec_rate;
                    regions.mayong.count++;
                } else {
                    regions.others.sum += rec_rate;
                    regions.others.count++;
                }
            }
        });
        
        return { scatterData: scatter, regionStats: regions };
    }, []);

    const gangnamRate = regionStats.gangnam.count ? (regionStats.gangnam.sum / regionStats.gangnam.count).toFixed(1) : "0.0";
    const mayongRate = regionStats.mayong.count ? (regionStats.mayong.sum / regionStats.mayong.count).toFixed(1) : "0.0";
    const othersRate = regionStats.others.count ? (regionStats.others.sum / regionStats.others.count).toFixed(1) : "0.0";

    const ScatterTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div style={{ background: '#111827', border: '1px solid #374151', padding: '16px', borderRadius: '8px', color: '#fff' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>{data.name}</div>
                    <div style={{ fontSize: '0.9rem', color: '#9CA3AF' }}>최근실거래: <span style={{ color: '#fff' }}>{data.recentStr}</span> (최고가 {data.highestStr})</div>
                    <div style={{ fontSize: '0.9rem', color: '#9CA3AF' }}>현재최저호가: <span style={{ color: '#fff' }}>{data.askStr}</span></div>
                    <div style={{ fontSize: '0.9rem', marginTop: '8px', color: data.mdd > -15 ? '#38BDF8' : '#F87171' }}>실거래 회복(MDD): {data.mdd}%</div>
                    <div style={{ fontSize: '0.9rem', color: data.gap > 0 ? '#38BDF8' : '#F87171' }}>호가 괴리율: {data.gap > 0 ? '+' : ''}{data.gap}%</div>
                </div>
            );
        }
        return null;
    };

    return (
        <div style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
            <div style={{ display: 'flex', flex: 1, paddingTop: '70px', paddingBottom: '90px' }}>
                <Sidebar activePath="/market" />
                <div style={{ flex: 1, padding: '40px', background: 'var(--bg-main)' }}>
                    {/* Header */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '40px', borderBottom: '1px solid var(--border-light)', paddingBottom: '16px' }}>
                        <div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px', marginBottom: '12px' }}>
                                TERMINAL BENCHMARK :: REALFIFTY LEADING 50 COMPOSITE
                            </div>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px' }}>
                                <span className="num-font" style={{ fontSize: '3rem', fontWeight: 900, color: '#fff' }}>{latestRecovery.toFixed(2)}</span>
                                <span className="num-font" style={{ fontSize: '1.2rem', color: 'var(--color-cyan)', fontWeight: 800 }}>▲ TRENDING</span>
                            </div>
                        </div>
                    </div>

                    {/* Top Row: Chart & Gauge */}
                    <div style={{ display: 'flex', gap: '20px', marginBottom: '40px', flexDirection: 'row', flexWrap: 'wrap' }}>
                        {/* Line Chart */}
                        <div style={{ flex: 2, background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px', minWidth: '400px' }}>
                            <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '24px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>✦ RealFifty 50 Leading Index Trajectory</span>
                                <span>100-DAY TRAILING</span>
                            </div>
                            <div style={{ height: '240px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={indexData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" vertical={false} />
                                        <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={11} tickFormatter={(tick) => tick.substring(5)} />
                                        <YAxis domain={['auto', 'auto']} stroke="var(--text-muted)" fontSize={11} width={40} />
                                        <RechartsTooltip contentStyle={{ background: '#111827', border: '1px solid #374151' }} />
                                        <Line type="monotone" dataKey="recovery" stroke="var(--color-cyan)" strokeWidth={3} dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Gauges */}
                        <div style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px', minWidth: '300px' }}>
                            <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '32px' }}>
                                실거래 회복률 분석 (CYCLE METRIC)
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                                {/* 강남3구 */}
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                        <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>강남 3구 (강남/서초/송파)</span>
                                        <span className="num-font" style={{ fontSize: '1rem', color: 'var(--color-cyan)', fontWeight: 800 }}>{gangnamRate}%</span>
                                    </div>
                                    <div style={{ height: '6px', background: '#374151', borderRadius: '3px', position: 'relative' }}>
                                        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${gangnamRate}%`, background: 'var(--color-cyan)', borderRadius: '3px' }}></div>
                                    </div>
                                </div>
                                {/* 마용성 */}
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                        <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>마용성 (마포/용산/성동)</span>
                                        <span className="num-font" style={{ fontSize: '1rem', color: 'var(--color-cyan)', fontWeight: 800 }}>{mayongRate}%</span>
                                    </div>
                                    <div style={{ height: '6px', background: '#374151', borderRadius: '3px', position: 'relative' }}>
                                        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${mayongRate}%`, background: 'var(--color-cyan)', borderRadius: '3px' }}></div>
                                    </div>
                                </div>
                                {/* 외곽 */}
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                        <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>노도강 외곽 벨트</span>
                                        <span className="num-font" style={{ fontSize: '1rem', color: 'var(--color-down)', fontWeight: 800 }}>{othersRate}%</span>
                                    </div>
                                    <div style={{ height: '6px', background: '#374151', borderRadius: '3px', position: 'relative' }}>
                                        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${othersRate}%`, background: 'var(--color-down)', borderRadius: '3px' }}></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Bottom Row: Scatter Plot & Volume */}
                    <div style={{ display: 'flex', gap: '20px', flexDirection: 'row', flexWrap: 'wrap' }}>
                        {/* Scatter Plot */}
                        <div style={{ flex: 2, background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px', minWidth: '600px' }}>
                            <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '24px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>REALFIFTY MARKET MAP (4분면 매트릭스)</span>
                                <span>DUAL-AXIS VALUATION RADAR</span>
                            </div>
                            <div style={{ height: '450px', position: 'relative' }}>
                                {/* Quadrant Labels */}
                                <div style={{ position: 'absolute', top: '10px', right: '20px', color: '#38BDF8', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT I: 신고가 랠리</div>
                                <div style={{ position: 'absolute', top: '10px', left: '20px', color: '#9CA3AF', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT II: 호가 방어 / 괴리 발생</div>
                                <div style={{ position: 'absolute', bottom: '20px', left: '20px', color: '#F87171', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT III: 과대 낙폭</div>
                                <div style={{ position: 'absolute', bottom: '20px', right: '20px', color: '#EAB308', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT IV: 급매 포착 구간</div>

                                <ResponsiveContainer width="100%" height="100%">
                                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                                        <CartesianGrid stroke="var(--border-light)" strokeDasharray="3 3" />
                                        <XAxis 
                                            type="number" 
                                            dataKey="mdd" 
                                            domain={[-35, 5]} 
                                            name="실거래 회복(MDD)" 
                                            unit="%" 
                                            stroke="var(--text-muted)" 
                                            fontSize={11}
                                            label={{ value: "◀ 실거래 하락 심각 (-35%)                      실거래 전고점 도달 (0%) ▶", position: "insideBottom", fill: "var(--text-muted)", fontSize: 10, dy: 15 }} 
                                        />
                                        <YAxis 
                                            type="number" 
                                            dataKey="gap" 
                                            domain={[-20, 30]} 
                                            name="호가 괴리율" 
                                            unit="%" 
                                            stroke="var(--text-muted)" 
                                            fontSize={11} 
                                        />
                                        <ZAxis type="number" range={[40, 40]} />
                                        <RechartsTooltip content={<ScatterTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                                        <ReferenceLine x={-15} stroke="var(--border-light)" strokeDasharray="3 3" />
                                        <ReferenceLine y={0} stroke="var(--border-light)" strokeDasharray="3 3" />
                                        
                                        {/* Colored Scatters by Quadrant logic */}
                                        <Scatter 
                                            data={scatterData} 
                                            shape="circle"
                                            isAnimationActive={false}
                                        >
                                            {scatterData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.fill} />
                                            ))}
                                        </Scatter>
                                    </ScatterChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Volume Bar Chart */}
                        <div style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px', minWidth: '300px' }}>
                            <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '24px' }}>
                                50대 단지 거래량 고갈 추이 (36-MONTH HISTORICAL VOLUME)
                            </div>
                            <div style={{ background: 'rgba(248, 113, 113, 0.1)', border: '1px solid var(--color-down)', padding: '12px', borderRadius: '4px', marginBottom: '24px' }}>
                                <div style={{ color: 'var(--color-down)', fontSize: '0.85rem', fontWeight: 800 }}>▲ 단 {latestVolume}건 체결로 유동성 증발.</div>
                            </div>
                            <div style={{ height: '300px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={volumeData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" vertical={false} />
                                        <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} tickFormatter={(val) => val.replace('20', '')} tick={{ fontSize: 9 }} interval={5} />
                                        <YAxis stroke="var(--text-muted)" fontSize={11} width={30} />
                                        <RechartsTooltip contentStyle={{ background: '#111827', border: '1px solid #374151' }} />
                                        <Bar dataKey="volume" fill="var(--color-cyan)" radius={[2, 2, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
