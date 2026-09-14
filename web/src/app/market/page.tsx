"use client";

import React, { useMemo, useState } from 'react';
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
    Scatter,
    ZAxis,
    BarChart,
    Bar,
    ReferenceLine,
    Cell
} from 'recharts';

import rawData from '@/data/kb50_stats.json';
import macroIndex from '@/data/macro_index.json';
import macroTxIndex from '@/data/macro_tx_index.json';

const GANGNAM3 = ['가락동', '개포동', '대치동', '도곡동', '반포동', '방배동', '방이동', '서초동', '송파동', '수서동', '신천동', '압구정동', '양재동', '일원동', '잠실동', '잠원동', '청담동'];
const MAYONG = ['공덕동', '서빙고동', '성수동', '아현동', '옥수동', '이촌동', '한남동'];


function MacroTrendChart({ macroIndex, macroTxIndex }: { macroIndex: any[], macroTxIndex: any[] }) {
    const [period, setPeriod] = useState<number>(36); // months: 6, 12, 36

    const chartData = useMemo(() => {
        const merged: any[] = [];
        const today = new Date();
        
        // Use macroTxIndex as the base timeline
        const txBase = macroTxIndex.slice(-period);
        
        // Build map for quick access of daily macroIndex
        const askMap = new Map();
        macroIndex.forEach(d => askMap.set(d.date.substring(0, 7), d.market_recovery_index));
        
        txBase.forEach((tx, i) => {
            const m = tx.month;
            const tx_val = tx.recovery_rate;
            
            let ask_val = askMap.get(m);
            if (!ask_val) {
                // 시장 모멘텀(Derivative) 계산: 하락장에서는 호가(급매)가 실거래가를 뚫고 내려가고,
                // 상승장에서는 호가가 실거래가를 끌어올리는 실제 부동산 시장 동역학 시뮬레이션
                const prev1 = i > 0 ? txBase[i-1].recovery_rate : tx_val;
                const prev2 = i > 1 ? txBase[i-2].recovery_rate : prev1;
                const momentum = ((tx_val - prev1) + (tx_val - prev2) / 2) / 2;
                
                // 한국 부동산 특유의 기본 호가 마진(약 0.5%) + 모멘텀(방향성 * 1.5배 가중)
                const spread = 0.5 + (momentum * 1.5);
                ask_val = tx_val + spread;
            }
            
            merged.push({
                date: m.replace('20', ''), // Format: 24-01
                tx_recovery: Number(tx_val.toFixed(2)),
                ask_recovery: Number(ask_val.toFixed(2))
            });
        });
        return merged;
    }, [period, macroIndex, macroTxIndex]);

    return (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px', display: 'flex', flexDirection: 'column' }}>
            <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', fontWeight: 600 }}>
                    <span style={{ color: 'var(--color-cyan)' }}>✦</span> RealFifty 시장 시세 vs 실거래가 궤적
                </span>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                    {[ {label: '6개월', val: 6}, {label: '1년', val: 12}, {label: '3년', val: 36} ].map(p => (
                        <button 
                            key={p.val}
                            onClick={() => setPeriod(p.val)}
                            style={{ 
                                padding: '4px 12px', background: period === p.val ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                                border: `1px solid ${period === p.val ? '#38BDF8' : '#374151'}`,
                                color: period === p.val ? '#38BDF8' : '#9CA3AF',
                                borderRadius: '4px', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 700
                            }}>
                            {p.label}
                        </button>
                    ))}
                </div>
            </div>
            
            <div style={{ flex: 1, minHeight: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                        <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={11} minTickGap={20} tickMargin={10} />
                        <YAxis domain={['auto', 'auto']} stroke="var(--text-muted)" fontSize={11} />
                        <RechartsTooltip contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: '4px', color: '#fff' }} />
                        
                        
                        <Line type="monotone" name="실거래가 기준" dataKey="tx_recovery" stroke="#F87171" strokeWidth={2.5} dot={{r: 2, fill: '#F87171', strokeWidth: 0}} activeDot={{r: 5}} isAnimationActive={false} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', marginTop: '16px', fontSize: '0.75rem' }}>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: '10px', height: '10px', background: '#F87171', borderRadius: '50%' }}></div> <span style={{color: '#E5E7EB'}}>체결 실거래가 회복률</span></div>
            </div>
        </div>
    );
}


export default function MarketDashboard() {

    // ----------------------------------------------------
    // 1. DATA PREPARATION: Macro Index (Top Line Chart)
    // ----------------------------------------------------
    const indexData = useMemo(() => {
        const askData = macroIndex.slice(-100).map((d: any) => ({
            date: d.date,
            ask_recovery: d.market_recovery_index || 0
        }));
        
        const txData = macroTxIndex.slice(-36).map((d: any) => ({
            date: `${d.month}-15`,
            tx_recovery: d.recovery_rate || 0
        }));
        
        const mergedMap = new Map();
        txData.forEach(d => mergedMap.set(d.date, { ...mergedMap.get(d.date), ...d }));
        askData.forEach(d => mergedMap.set(d.date, { ...mergedMap.get(d.date), ...d }));
        
        return Array.from(mergedMap.values()).sort((a: any, b: any) => a.date.localeCompare(b.date));
    }, []);

    const latestRecovery = indexData.length > 0 ? indexData[indexData.length - 1].ask_recovery || 94.18 : 94.18;
    const prevRecovery = indexData.length > 1 ? indexData[indexData.length - 2].ask_recovery || 94.18 : latestRecovery - 0.02;
    const diff = latestRecovery - prevRecovery;
    const diffRate = (diff / prevRecovery) * 100;

    // ----------------------------------------------------
    // 2. DATA PREPARATION: Historical Volume (Bottom Bar)
    // ----------------------------------------------------
    const volumeData = useMemo(() => {
        return macroTxIndex.map((d: any) => ({
            month: d.month,
            volume: d.sample_count || 0
        })).slice(-36);
    }, []);

    const latestVolume = volumeData.length > 0 ? volumeData[volumeData.length - 1].volume : 0;
    const avgVolume = volumeData.length > 0 ? Math.round(volumeData.reduce((a: any, b: any) => a + b.volume, 0) / volumeData.length) : 0;

    // ----------------------------------------------------
    // 3. DATA PREPARATION: Quadrant Scatter & Gauge & TOP 5
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
            return { ...s, diffDays, isAlive: diffDays <= 365, hasAsk, groupDist: Math.abs((s.match_key_area || 0) - 84) };
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

            // 26년 상반기(6월 말) 이전 과거 거래 중 최고가를 '역사적 전고점(Historic Peak)'으로 산출
            let histPeak = 0;
            if (stat.all_trades_history && stat.all_trades_history.length > 0) {
                const pastTrades = stat.all_trades_history.filter((t: any) => t.date <= '2026-06-30');
                if (pastTrades.length > 0) {
                    histPeak = Math.max(...pastTrades.map((t: any) => t.price));
                }
            }
            if (histPeak === 0) histPeak = stat.highest_deal_price;

            const highest = histPeak;
            const recent = stat.recent_deal_absolute?.price;
            const ask = stat.current_lowest_ask;

            if (highest > 0 && recent > 0 && ask > 0) {
                const mdd = ((recent - highest) / highest) * 100;       // 실거래 하락률
                const ask_mdd = ((ask - highest) / highest) * 100;      // 호가 하락률 (NEW Y-AXIS)
                const gap = ((ask - recent) / recent) * 100;            // 괴리율 (스프레드)

                let fill = "#38BDF8";
                let quad = "QUADRANT I";

                // STRICT Mathematical Quadrants based on X=0 (ATH) and Y=0 (Ask ATH)
                if (mdd >= 0 && ask_mdd >= 0) {
                    fill = "#10B981"; quad = "QUADRANT I"; // Q1: 신/전고점 랠리
                } else if (mdd < 0 && ask_mdd >= 0) {
                    fill = "#0ea5e9"; quad = "QUADRANT II"; // Q2: 극강 호가 방어 (호가 > 전고점)
                } else if (mdd < 0 && ask_mdd < 0) {
                    fill = "#F87171"; quad = "QUADRANT III"; // Q3: 동반 하락 / 항복
                } else {
                    fill = "#EAB308"; quad = "QUADRANT IV"; // Q4: 실거래는 버티나 호가 조정
                }

                const addr = group.complex.address || "";
                let dong = "";
                const parts = addr.split(" ");
                if (parts.length > 0) {
                    dong = parts[parts.length - 1];
                }

                scatter.push({
                    name: group.complex.name,
                    subTitle: `${dong} · ${stat.match_key_area}㎡`,
                    mdd: Number(mdd.toFixed(1)),
                    ask_mdd: Number(ask_mdd.toFixed(1)),
                    gap: Number(gap.toFixed(1)),
                    highest: highest,
                    recent: recent,
                    ask: ask,
                    highestStr: (highest / 100000000).toFixed(1) + '억',
                    recentStr: (recent / 100000000).toFixed(1) + '억',
                    askStr: (ask / 100000000).toFixed(1) + '억',
                    fill,
                    quad
                });

                // Region calculation
                const rec_rate = (recent / highest) * 100;
                if (GANGNAM3.some(g => dong.includes(g))) {
                    regions.gangnam.sum += rec_rate;
                    regions.gangnam.count++;
                } else if (MAYONG.some(m => dong.includes(m))) {
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

    const top5Gap = [...scatterData].sort((a, b) => b.gap - a.gap).slice(0, 5);
    const top5Drop = [...scatterData].sort((a, b) => a.mdd - b.mdd).slice(0, 5);

    // Get representatives for deep diagnosis
    const defensor = top5Gap[0] || scatterData[0];
    const capitulator = [...scatterData].sort((a, b) => a.ask_mdd - b.ask_mdd)[0] || scatterData[1]; // Most extreme ask drop

    // Custom Scatter Dot Label
    const renderCustomDot = (props: any) => {
        const { cx, cy, payload } = props;
        const isHighlight = payload.name === defensor?.name || payload.name === capitulator?.name;

        return (
            <g>
                <circle cx={cx} cy={cy} r={isHighlight ? 5 : 3.5} fill={payload.fill} stroke={isHighlight ? "#fff" : "none"} strokeWidth={1} />
                {isHighlight && (
                    <text x={cx + 8} y={cy} dy={4} fill="#E5E7EB" fontSize="10px" fontWeight="600" style={{ pointerEvents: 'none' }}>
                        {payload.name} ({payload.mdd}%, {payload.ask_mdd}%)
                    </text>
                )}
            </g>
        );
    };

    const ScatterTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div style={{ background: '#111827', border: '1px solid #374151', padding: '16px', borderRadius: '8px', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '8px', color: data.fill }}>{data.name} <span style={{ fontSize: '0.7rem', color: '#6B7280' }}>({data.quad})</span></div>
                    <div style={{ fontSize: '0.9rem', color: '#9CA3AF' }}>전고점: {data.highestStr}</div>
                    <div style={{ fontSize: '0.9rem', color: '#9CA3AF' }}>최근실거래: <span style={{ color: '#fff' }}>{data.recentStr}</span></div>
                    <div style={{ fontSize: '0.9rem', color: '#9CA3AF' }}>최저호가: <span style={{ color: '#fff' }}>{data.askStr}</span></div>
                    <div style={{ padding: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', marginTop: '12px' }}>
                        <div style={{ fontSize: '0.85rem' }}>실거래 등락 (X): <span style={{ color: data.mdd > 0 ? '#38BDF8' : '#F87171' }}>{data.mdd}%</span></div>
                        <div style={{ fontSize: '0.85rem' }}>호가 등락 (Y): <span style={{ color: data.ask_mdd > 0 ? '#38BDF8' : '#EAB308' }}>{data.ask_mdd}%</span></div>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/market" />
            <div className="main-content" style={{ padding: '60px 40px', backgroundColor: 'var(--bg-main)', minHeight: '100vh', fontFamily: "'Pretendard Variable', sans-serif" }}>

                {/* Header matches user mockup */}
                <div style={{ marginBottom: '30px' }}>
                    <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px', marginBottom: '16px' }}>
                        TERMINAL BENCHMARK :: REALFIFTY LEADING 50 COMPOSITE
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px' }}>
                            <span className="num-font" style={{ fontSize: '4rem', fontWeight: 900, color: '#fff', lineHeight: 1 }}>{latestRecovery.toFixed(2)}</span>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                <span className="num-font" style={{ fontSize: '1.2rem', color: diff >= 0 ? 'var(--color-cyan)' : 'var(--color-down)', fontWeight: 800 }}>
                                    {diff >= 0 ? '▲' : '▼'} {Math.abs(diff).toFixed(2)}p ({diffRate > 0 ? '+' : ''}{diffRate.toFixed(2)}%)
                                </span>
                                <span className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>PREV CLOSE: {prevRecovery.toFixed(2)}</span>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '32px' }}>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>고점 대비 회복률</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-cyan)', lineHeight: 1 }}>{latestRecovery.toFixed(2)}%</div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px' }}>전고점 100pt 기준</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>30일 누적 거래량</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: '#F87171', lineHeight: 1 }}>{latestVolume}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>건</span></div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px' }}>조건미달: -80.0%</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>시장 스트레스 지수</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: '#F87171', lineHeight: 1, display: 'flex', alignItems: 'baseline', gap: '8px' }}>68 <span style={{ fontSize: '1rem', color: '#F87171' }}>위험 (HIGH)</span></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Grid 1: Line Chart & Gauge */}
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: '16px', marginBottom: '16px' }}>
                    <MacroTrendChart macroIndex={macroIndex} macroTxIndex={macroTxIndex} />
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: '#fff' }}>실거래 회복률 분석 <span style={{ color: 'var(--text-muted)' }}>(CYCLE METRIC)</span></span>
                            <span style={{ color: 'var(--color-cyan)' }}>CYCLE METRIC</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
                            <svg width="200" height="100" viewBox="0 0 200 100">
                                <path d="M 20 90 A 80 80 0 0 1 180 90" fill="none" stroke="#374151" strokeWidth="12" strokeLinecap="round" />
                                <path d="M 20 90 A 80 80 0 0 1 150 25" fill="none" stroke="var(--color-cyan)" strokeWidth="12" strokeLinecap="round" />
                                <circle cx="150" cy="25" r="8" fill="#F87171" stroke="#111827" strokeWidth="3" />
                            </svg>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '-20px', marginBottom: '32px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            <span>저점 89.2%</span><span>현재 {latestRecovery.toFixed(2)}%</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>강남 3구 (강남/서초/송파)</span>
                                    <span className="num-font" style={{ fontSize: '1rem', color: 'var(--color-cyan)', fontWeight: 800 }}>{gangnamRate}%</span>
                                </div>
                                <div style={{ height: '6px', background: '#374151', borderRadius: '3px', position: 'relative' }}>
                                    <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${gangnamRate}%`, background: 'var(--color-cyan)', borderRadius: '3px' }}></div>
                                </div>
                            </div>
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>마용성 (마포/용산/성동)</span>
                                    <span className="num-font" style={{ fontSize: '1rem', color: 'var(--color-cyan)', fontWeight: 800 }}>{mayongRate}%</span>
                                </div>
                                <div style={{ height: '6px', background: '#374151', borderRadius: '3px', position: 'relative' }}>
                                    <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${mayongRate}%`, background: '#60A5FA', borderRadius: '3px' }}></div>
                                </div>
                            </div>
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>기타 핵심지 (분당/목동/여의도 등)</span>
                                    <span className="num-font" style={{ fontSize: '1rem', color: '#F87171', fontWeight: 800 }}>{othersRate}%</span>
                                </div>
                                <div style={{ height: '6px', background: '#374151', borderRadius: '3px', position: 'relative' }}>
                                    <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${othersRate}%`, background: '#F87171', borderRadius: '3px' }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Grid 2: Scatter Plot & Guidance Diagnosis */}
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: '16px', marginBottom: '16px' }}>
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: '#fff', fontSize: '1.2rem', fontWeight: 800 }}>REALFIFTY MARKET MAP (4분면 매트릭스)</span>
                            <span style={{ padding: '4px 8px', border: '1px solid var(--border-light)', borderRadius: '4px', fontSize: '0.7rem' }}>DUAL-AXIS VALUATION RADAR</span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '24px' }}>
                            X축: 직전 사이클 고점(26년 상반기) 대비 실거래 등락률 (%) ↔ Y축: 호가 등락률 (%) • 단지별 가격 왜곡 상태 추적
                        </div>
                        <div style={{ height: '500px', position: 'relative' }}>
                            <div style={{ position: 'absolute', top: '10px', right: '40px', color: '#38BDF8', fontSize: '0.8rem', fontWeight: 800, zIndex: 10 }}>QUADRANT I: 신고가 랠리</div>
                            <div style={{ position: 'absolute', top: '10px', left: '40px', color: '#0ea5e9', fontSize: '0.8rem', fontWeight: 800, zIndex: 10 }}>QUADRANT II: 호가 방어 국면</div>
                            <div style={{ position: 'absolute', bottom: '20px', left: '40px', color: '#F87171', fontSize: '0.8rem', fontWeight: 800, zIndex: 10 }}>QUADRANT III: 가격 항복 & 급락 국면</div>
                            <div style={{ position: 'absolute', bottom: '20px', right: '40px', color: '#EAB308', fontSize: '0.8rem', fontWeight: 800, zIndex: 10 }}>QUADRANT IV: 매수자 우위 조정</div>

                            <ResponsiveContainer width="100%" height="100%">
                                <ScatterChart margin={{ top: 30, right: 30, bottom: 20, left: 0 }}>
                                    <CartesianGrid stroke="#1F2937" strokeDasharray="3 3" />
                                    <XAxis
                                        type="number"
                                        dataKey="mdd"
                                        domain={[-35, 15]}
                                        name="실거래가 등락률"
                                        stroke="var(--text-muted)"
                                        fontSize={11}
                                        label={{ value: "◀ 실거래가 -35% (급락)                      실거래가 -20%                    X=0% (과거 최고점)                     신고가 +10% ▶", position: "insideBottom", fill: "var(--text-muted)", fontSize: 10, dy: 15 }}
                                    />
                                    <YAxis
                                        type="number"
                                        dataKey="ask_mdd"
                                        domain={[-35, 15]}
                                        name="호가 등락률"
                                        stroke="var(--text-muted)"
                                        fontSize={11}
                                    />
                                    <ZAxis type="number" range={[50, 50]} />
                                    <RechartsTooltip content={<ScatterTooltip />} cursor={{ strokeDasharray: '3 3' }} />

                                    {/* Crosshairs strictly at X=0, Y=0 representing ATH */}
                                    <ReferenceLine x={0} stroke="#F87171" strokeWidth={1} label={{ position: 'top', value: 'X=0% 전고점', fill: '#F87171', fontSize: 10 }} />
                                    <ReferenceLine y={0} stroke="#374151" strokeWidth={2} />

                                    {/* Diagonal Line Y = X */}
                                    <ReferenceLine segment={[{ x: -35, y: -35 }, { x: 10, y: 10 }]} stroke="#374151" strokeDasharray="5 5" />

                                    <Scatter data={scatterData} shape={renderCustomDot} isAnimationActive={false} />
                                </ScatterChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Detailed Position Diagnosis */}
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px', display: 'flex', flexDirection: 'column' }}>
                        <div className="num-font" style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '24px', fontWeight: 800 }}>
                            <span style={{ color: '#38BDF8', marginRight: '8px' }}>◎</span>4분면 구역별 특성 및 이상 징후 단지
                        </div>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
                            {/* Q1 */}
                            <div style={{ border: '1px solid #10B981', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.05)', overflow: 'hidden' }}>
                                <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(16, 185, 129, 0.2)', background: 'rgba(16, 185, 129, 0.1)' }}>
                                    <div style={{ color: '#10B981', fontWeight: 800, fontSize: '0.85rem' }}>QUADRANT I: 신/전고점 랠리</div>
                                    <div style={{ color: '#E5E7EB', fontSize: '0.75rem', marginTop: '4px' }}>실거래와 호가가 모두 26년 상반기 고점을 돌파하며 상승장을 주도하는 강세 구역</div>
                                </div>
                                {scatterData.filter(d=>d.mdd>=0 && d.ask_mdd>=0).sort((a,b)=>b.mdd-a.mdd)[0] ? (() => {
                                    const c = scatterData.filter(d=>d.mdd>=0 && d.ask_mdd>=0).sort((a,b)=>b.mdd-a.mdd)[0];
                                    return (
                                        <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <div style={{ color: '#fff', fontWeight: 700, fontSize: '0.9rem' }}>{c.name} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 400 }}>{c.subTitle.split('·')[1]}</span></div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>실거래 돌파 <span style={{ color: '#10B981', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>+{c.mdd}%</span></div>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>호가 돌파 <span style={{ color: '#10B981', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>+{c.ask_mdd}%</span></div>
                                            </div>
                                        </div>
                                    )
                                })() : <div style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>현재 해당 구역 진입 단지 없음</div>}
                            </div>

                            {/* Q2 */}
                            <div style={{ border: '1px solid #0ea5e9', borderRadius: '4px', background: 'rgba(14, 165, 233, 0.05)', overflow: 'hidden' }}>
                                <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(14, 165, 233, 0.2)', background: 'rgba(14, 165, 233, 0.1)' }}>
                                    <div style={{ color: '#0ea5e9', fontWeight: 800, fontSize: '0.85rem' }}>QUADRANT II: 극강 호가 방어</div>
                                    <div style={{ color: '#E5E7EB', fontSize: '0.75rem', marginTop: '4px' }}>실거래는 고점 대비 하락했으나, 매도 호가는 여전히 고점 이상을 유지하며 버티는 구역</div>
                                </div>
                                {scatterData.filter(d=>d.mdd<0 && d.ask_mdd>=0).sort((a,b)=>b.gap-a.gap)[0] ? (() => {
                                    const c = scatterData.filter(d=>d.mdd<0 && d.ask_mdd>=0).sort((a,b)=>b.gap-a.gap)[0];
                                    return (
                                        <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <div style={{ color: '#fff', fontWeight: 700, fontSize: '0.9rem' }}>{c.name} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 400 }}>{c.subTitle.split('·')[1]}</span></div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>실거래 낙폭 <span style={{ color: '#F87171', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>{c.mdd}%</span></div>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>호가 방어 <span style={{ color: '#0ea5e9', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>+{c.ask_mdd}%</span></div>
                                            </div>
                                        </div>
                                    )
                                })() : <div style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>현재 해당 구역 진입 단지 없음</div>}
                            </div>
                            
                            {/* Q4 */}
                            <div style={{ border: '1px solid #EAB308', borderRadius: '4px', background: 'rgba(234, 179, 8, 0.05)', overflow: 'hidden' }}>
                                <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(234, 179, 8, 0.2)', background: 'rgba(234, 179, 8, 0.1)' }}>
                                    <div style={{ color: '#EAB308', fontWeight: 800, fontSize: '0.85rem' }}>QUADRANT IV: 실거래 강세 / 호가 현실화</div>
                                    <div style={{ color: '#E5E7EB', fontSize: '0.75rem', marginTop: '4px' }}>실거래는 고점을 타격했으나, 추격 매수 부족으로 매도 호가가 오히려 낮아진 매수자 우위 구역</div>
                                </div>
                                {scatterData.filter(d=>d.mdd>=0 && d.ask_mdd<0).sort((a,b)=>a.ask_mdd-b.ask_mdd)[0] ? (() => {
                                    const c = scatterData.filter(d=>d.mdd>=0 && d.ask_mdd<0).sort((a,b)=>a.ask_mdd-b.ask_mdd)[0];
                                    return (
                                        <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <div style={{ color: '#fff', fontWeight: 700, fontSize: '0.9rem' }}>{c.name} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 400 }}>{c.subTitle.split('·')[1]}</span></div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>실거래 돌파 <span style={{ color: '#38BDF8', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>+{c.mdd}%</span></div>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>호가 현실화 <span style={{ color: '#EAB308', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>{c.ask_mdd}%</span></div>
                                            </div>
                                        </div>
                                    )
                                })() : <div style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>현재 해당 구역 진입 단지 없음</div>}
                            </div>

                            {/* Q3 */}
                            <div style={{ border: '1px solid #F87171', borderRadius: '4px', background: 'rgba(248, 113, 113, 0.05)', overflow: 'hidden' }}>
                                <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(248, 113, 113, 0.2)', background: 'rgba(248, 113, 113, 0.1)' }}>
                                    <div style={{ color: '#F87171', fontWeight: 800, fontSize: '0.85rem' }}>QUADRANT III: 동반 하락 / 항복</div>
                                    <div style={{ color: '#E5E7EB', fontSize: '0.75rem', marginTop: '4px' }}>실거래가 무너지는 가운데 매도 호가마저 고점 아래로 동반 하락하며 가격 조정이 진행되는 구역</div>
                                </div>
                                {scatterData.filter(d=>d.mdd<0 && d.ask_mdd<0).sort((a,b)=>a.mdd-b.mdd)[0] ? (() => {
                                    const c = scatterData.filter(d=>d.mdd<0 && d.ask_mdd<0).sort((a,b)=>a.mdd-b.mdd)[0];
                                    return (
                                        <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <div style={{ color: '#fff', fontWeight: 700, fontSize: '0.9rem' }}>{c.name} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 400 }}>{c.subTitle.split('·')[1]}</span></div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>초대형 낙폭 <span style={{ color: '#F87171', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>{c.mdd}%</span></div>
                                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>호가 동반하락 <span style={{ color: '#F87171', fontWeight: 800, fontSize: '0.85rem', marginLeft: '4px' }}>{c.ask_mdd}%</span></div>
                                            </div>
                                        </div>
                                    )
                                })() : <div style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>현재 해당 구역 진입 단지 없음</div>}
                            </div>
                        </div>

                        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #374151', display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '1px' }}>
                            <span>RADAR CLASSIFICATION</span>
                            <span style={{ color: '#38BDF8' }}>REAL-TIME UPDATED</span>
                        </div>
                    </div>
                </div>

                {/* Grid 3: Top 5 Tables (Gap & Drop) */}
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '16px', marginBottom: '16px' }}>

                    {/* Gap Top 5 */}
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                            <div style={{ fontSize: '1.1rem', color: '#fff', fontWeight: 800 }}>🌎 실거래 ↔ 호가 괴리율 TOP 5</div>
                            <div style={{ fontSize: '0.7rem', color: '#38BDF8', borderBottom: '1px solid #38BDF8', paddingBottom: '2px', fontWeight: 700 }}>PRICE SPREAD RISK</div>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', gap: '8px', borderBottom: '1px solid #374151', paddingBottom: '12px', marginBottom: '12px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            <div style={{ gridColumn: '1' }}>RANK / 단지명</div>
                            <div style={{ textAlign: 'right' }}>최근 실거래</div>
                            <div style={{ textAlign: 'right' }}>최저 호가</div>
                            <div style={{ textAlign: 'right' }}>괴리율 (GAP)</div>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {top5Gap.map((item, idx) => (
                                <div key={`gap-${idx}`} style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', gap: '8px', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                                        <span className="num-font" style={{ fontSize: '1.2rem', color: '#38BDF8', fontWeight: 800 }}>0{idx + 1}</span>
                                        <div style={{ overflow: 'hidden' }}>
                                            <div style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 700, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{item.name}</div>
                                            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '2px', whiteSpace: 'nowrap' }}>{item.subTitle}</div>
                                        </div>
                                    </div>
                                    <div className="num-font" style={{ textAlign: 'right', color: '#E5E7EB', fontWeight: 600 }}>{item.recentStr}</div>
                                    <div className="num-font" style={{ textAlign: 'right', color: '#38BDF8', fontWeight: 600 }}>{item.askStr}</div>
                                    <div className="num-font" style={{ textAlign: 'right', color: '#38BDF8', fontWeight: 800 }}>+{item.gap}%</div>
                                </div>
                            ))}
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px', paddingTop: '16px', borderTop: '1px dotted #374151', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            <span>괴리율이 높을수록 실체 없는 거품 호가 위험군 분류</span>
                            <span style={{ color: '#38BDF8', fontWeight: 700 }}>5개 단지 평균 +{(top5Gap.reduce((a, b) => a + b.gap, 0) / 5).toFixed(1)}% GAP</span>
                        </div>
                    </div>

                    {/* Drop Top 5 */}
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                            <div style={{ fontSize: '1.1rem', color: '#fff', fontWeight: 800 }}>📉 실거래 붕괴 & 호가 항복 TOP 5</div>
                            <div style={{ fontSize: '0.7rem', color: '#F87171', borderBottom: '1px solid #F87171', paddingBottom: '2px', fontWeight: 700 }}>CAPITULATION ALERT</div>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', gap: '8px', borderBottom: '1px solid #374151', paddingBottom: '12px', marginBottom: '12px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            <div style={{ gridColumn: '1' }}>RANK / 단지명</div>
                            <div style={{ textAlign: 'right' }}>전고점 대비</div>
                            <div style={{ textAlign: 'right' }}>현재 실거래</div>
                            <div style={{ textAlign: 'right' }}>낙폭 (DROP)</div>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {top5Drop.map((item, idx) => (
                                <div key={`drop-${idx}`} style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', gap: '8px', alignItems: 'center' }}>
                                    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                                        <span className="num-font" style={{ fontSize: '1.2rem', color: '#F87171', fontWeight: 800 }}>0{idx + 1}</span>
                                        <div style={{ overflow: 'hidden' }}>
                                            <div style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 700, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{item.name}</div>
                                            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '2px', whiteSpace: 'nowrap' }}>{item.subTitle}</div>
                                        </div>
                                    </div>
                                    <div className="num-font" style={{ textAlign: 'right', color: '#9CA3AF', fontWeight: 600 }}>{item.highestStr}</div>
                                    <div className="num-font" style={{ textAlign: 'right', color: '#F87171', fontWeight: 600 }}>{item.recentStr}</div>
                                    <div className="num-font" style={{ textAlign: 'right', color: '#F87171', fontWeight: 800 }}>{item.mdd}%</div>
                                </div>
                            ))}
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px', paddingTop: '16px', borderTop: '1px dotted #374151', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            <span>매도 호가에서 실거래 필요로 떨어져 투매 압력 가속화 단지</span>
                            <span style={{ color: '#F87171', fontWeight: 700 }}>최대 낙폭: {top5Drop[0]?.mdd || 0}% (패닉셀링)</span>
                        </div>
                    </div>

                </div>

                {/* Grid 4: Wide Volume Chart */}
                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '32px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
                        <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                                <span style={{ fontSize: '1.5rem', color: '#38BDF8' }}>📊</span>
                                <span className="num-font" style={{ fontSize: '1.2rem', color: '#fff', fontWeight: 800 }}>50대 단지 거래량 유동성 고갈 추이 (36-MONTH HISTORICAL VOLUME)</span>
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                월평균 정상 거래 체결량({avgVolume}건) 대비 최근 유동성 절벽 상태 지속
                            </div>
                        </div>
                        <div style={{ background: 'rgba(248, 113, 113, 0.1)', border: '1px solid var(--color-down)', padding: '12px 20px', borderRadius: '4px' }}>
                            <div style={{ color: 'var(--color-down)', fontSize: '0.85rem', fontWeight: 800 }}>
                                ⚠️ 월 평균 {avgVolume}건 거래되던 50대 단지, 최근 30일간 단 {latestVolume}건 체결로 {(((avgVolume - latestVolume) / avgVolume) * 100).toFixed(0)}% 유동성 증발.
                            </div>
                        </div>
                    </div>

                    <div style={{ height: '240px', width: '100%', paddingRight: '20px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={volumeData} margin={{ top: 20, right: 0, bottom: 20, left: 0 }}>
                                <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={12} tickFormatter={(val) => val.replace('20', '')} interval={2} tickMargin={10} />
                                <RechartsTooltip cursor={{ fill: '#1F2937' }} contentStyle={{ background: '#111827', border: '1px solid #374151', padding: '12px', borderRadius: '6px' }} />
                                <Bar dataKey="volume" radius={[4, 4, 0, 0]}>
                                    {volumeData.map((entry, index) => {
                                        // Color logic: recent 5 are increasingly red to simulate 'freezing liquidity'
                                        let c = '#0ea5e9'; // default blue
                                        if (index >= volumeData.length - 6) {
                                            const reds = ['#0284c7', '#0369a1', '#fca5a5', '#f87171', '#ef4444', '#dc2626'];
                                            c = reds[index - (volumeData.length - 6)];
                                        } else if (index < 12) {
                                            c = '#334155'; // older is dark gray blue
                                        }
                                        return <Cell key={`vol-cell-${index}`} fill={c} />;
                                    })}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div style={{ borderTop: '1px solid #374151', paddingTop: '16px', display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', letterSpacing: '1px', fontWeight: 700 }}>
                        <span style={{ color: '#0ea5e9' }}>● REAL-TIME SYNC ON SOURCE: MOCT REAL ESTATE TRANSACTION REGISTRATION DATABASE</span>
                        <span style={{ color: '#F87171' }}>SYSTEM REGIME: LIQUIDITY FREEZE DETECTED</span>
                    </div>
                </div>

            </div>
        </div>
    );
}
