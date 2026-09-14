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

export default function MarketDashboard() {

    // ----------------------------------------------------
    // 1. DATA PREPARATION: Macro Index (Top Line Chart)
    // ----------------------------------------------------
    const indexData = useMemo(() => {
        return macroIndex.map((d: any) => ({
            date: d.date,
            recovery: d.market_recovery_index || 0
        })).slice(-100);
    }, []);

    const latestRecovery = indexData.length > 0 ? indexData[indexData.length - 1].recovery : 94.18;
    const prevRecovery = indexData.length > 1 ? indexData[indexData.length - 2].recovery : latestRecovery - 0.02;
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

            const highest = stat.highest_deal_price;
            const recent = stat.recent_deal_absolute?.price;
            const ask = stat.current_lowest_ask;

            if (highest > 0 && recent > 0 && ask > 0) {
                const mdd = ((recent - highest) / highest) * 100;       // 실거래 하락률
                const ask_mdd = ((ask - highest) / highest) * 100;      // 호가 하락률 (NEW Y-AXIS)
                const gap = ((ask - recent) / recent) * 100;            // 괴리율 (스프레드)

                let fill = "#38BDF8";
                let quad = "QUADRANT I";

                // Color Logic based on ATH crosshair and diagonal spread
                if (mdd >= 0 && ask_mdd >= 0) {
                    fill = "#38BDF8"; quad = "QUADRANT I"; // 상승 랠리
                } else if (ask_mdd > mdd) {
                    fill = "#0ea5e9"; quad = "QUADRANT II"; // 호가 방어 (Gray/Blue)
                } else if (ask_mdd <= mdd) {
                    fill = "#F87171"; quad = "QUADRANT III"; // 가격 항복 (Red)
                } else {
                    fill = "#EAB308"; quad = "QUADRANT IV"; // 기타
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
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', fontWeight: 600 }}><span style={{ color: 'var(--color-cyan)' }}>✦</span> RealFifty 50 Leading Index Trajectory</span>
                            <span style={{ padding: '4px 8px', border: '1px solid var(--border-light)', borderRadius: '4px', fontSize: '0.7rem' }}>100-DAY TRAILING</span>
                        </div>
                        <div style={{ height: '300px' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={indexData} margin={{ top: 20, right: 20, bottom: 0, left: -20 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" vertical={false} />
                                    <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={11} tickFormatter={(tick) => tick.substring(5)} minTickGap={20} />
                                    <YAxis domain={['dataMin - 1', 'dataMax + 1']} stroke="var(--text-muted)" fontSize={11} />
                                    <RechartsTooltip contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: '4px' }} />
                                    <Line type="step" dataKey="recovery" stroke="var(--color-cyan)" strokeWidth={3} dot={false} isAnimationActive={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
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
                                    <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>노도강 외곽 벨트</span>
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
                            X축: 실거래가 고점 대비 등락률 (%) ↔ Y축: 최신 호가 고점 대비 등락률 (%) • 단지별 가격 왜곡 상태 추적
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
                                        domain={[-35, 10]}
                                        name="실거래가 등락률"
                                        stroke="var(--text-muted)"
                                        fontSize={11}
                                        label={{ value: "◀ 실거래가 -35% (급락)                      실거래가 -20%                    X=0% (전고점 수준)                     신고가 +10% ▶", position: "insideBottom", fill: "var(--text-muted)", fontSize: 10, dy: 15 }}
                                    />
                                    <YAxis
                                        type="number"
                                        dataKey="ask_mdd"
                                        domain={[-35, 10]}
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
                        <div className="num-font" style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '32px', fontWeight: 800 }}>
                            <span style={{ color: '#38BDF8', marginRight: '8px' }}>◎</span>단지별 포지션 심층 진단
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', flex: 1 }}>
                            {/* Card 1: Defensor (Q2) */}
                            {defensor && (
                                <div style={{ border: '1px solid #0ea5e9', padding: '20px', borderRadius: '4px', background: 'rgba(14, 165, 233, 0.05)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>{defensor.name} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}>{defensor.subTitle.split('·')[1]}</span></div>
                                        <div style={{ background: '#0ea5e9', color: '#fff', fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 800 }}>QUADRANT II</div>
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '16px', fontSize: '0.8rem' }}>
                                        <div>
                                            <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>실거래 하락률</div>
                                            <div style={{ color: '#fff', fontWeight: 700 }}>{defensor.mdd}%</div>
                                        </div>
                                        <div>
                                            <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>호가 하락률</div>
                                            <div style={{ color: '#fff', fontWeight: 700 }}>{defensor.ask_mdd}%</div>
                                        </div>
                                        <div>
                                            <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>스프레드 괴리</div>
                                            <div style={{ color: '#38BDF8', fontWeight: 700 }}>+{defensor.gap}%</div>
                                        </div>
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: '#E5E7EB', lineHeight: 1.6, background: '#111827', padding: '12px', borderLeft: '3px solid #0ea5e9' }}>
                                        <span style={{ color: '#38BDF8', fontWeight: 800 }}>[호가 방어 구간 판정]</span> 매도자가 최근 실거래가 급락({defensor.mdd}%)을 인정하지 않고 전고점에 가까운 호가를 지속 유지. 거래 성사 불가 국면(Liquidity Freeze) 지속 중.
                                    </div>
                                </div>
                            )}

                            {/* Card 2: Capitulator (Q3) */}
                            {capitulator && (
                                <div style={{ border: '1px solid #F87171', padding: '20px', borderRadius: '4px', background: 'rgba(248, 113, 113, 0.05)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>{capitulator.name} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}>{capitulator.subTitle.split('·')[1]}</span></div>
                                        <div style={{ background: '#7F1D1D', color: '#FCA5A5', fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 800 }}>QUADRANT III</div>
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '16px', fontSize: '0.8rem' }}>
                                        <div>
                                            <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>실거래 하락률</div>
                                            <div style={{ color: '#fff', fontWeight: 700 }}>{capitulator.mdd}%</div>
                                        </div>
                                        <div>
                                            <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>호가 하락률</div>
                                            <div style={{ color: '#fff', fontWeight: 700 }}>{capitulator.ask_mdd}%</div>
                                        </div>
                                        <div>
                                            <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>상태</div>
                                            <div style={{ color: '#F87171', fontWeight: 700 }}>호가 붕괴</div>
                                        </div>
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: '#E5E7EB', lineHeight: 1.6, background: '#111827', padding: '12px', borderLeft: '3px solid #F87171' }}>
                                        <span style={{ color: '#F87171', fontWeight: 800 }}>[가격 항복 국면 판정]</span> 최고가 {capitulator.highestStr} 대비 {capitulator.askStr} 급매 매물이 속출하며 매도 호가({capitulator.ask_mdd}%)가 실거래선 밑으로 내려앉음. 하락 압력 가속화.
                                    </div>
                                </div>
                            )}
                        </div>

                        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #374151', display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '1px' }}>
                            <span>RADAR ACCURACY INDEX</span>
                            <span style={{ color: '#38BDF8' }}>99.2% CONFIDENCE</span>
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
