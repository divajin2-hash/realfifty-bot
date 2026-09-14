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
    // 2. DATA PREPARATION: Historical Volume (Bottom Right Bar)
    // ----------------------------------------------------
    const volumeData = useMemo(() => {
        return macroTxIndex.map((d: any) => ({
            month: d.month,
            volume: d.sample_count || 0
        })).slice(-36);
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
            return { ...s, diffDays, isAlive: diffDays <= 365, hasAsk, groupDist: Math.abs((s.match_key_area||0) - 84) };
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
                const mdd = ((recent - highest) / highest) * 100;
                const gap = ((ask - recent) / recent) * 100;
                
                let fill = "#38BDF8";
                if (mdd >= -15 && gap >= 0) fill = "#38BDF8"; // Q1: cyan
                else if (mdd >= -15 && gap < 0) fill = "#9CA3AF"; // Q2: gray
                else if (mdd < -15 && gap < 0) fill = "#F87171"; // Q3: red
                else fill = "#EAB308"; // Q4: yellow
                
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
                let dong = "";
                const parts = addr.split(" ");
                if (parts.length > 0) {
                    dong = parts[parts.length - 1]; // e.g. 가락동
                }
                
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

    const ScatterTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div style={{ background: '#111827', border: '1px solid #374151', padding: '16px', borderRadius: '8px', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}>
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
        <div className="app-wrapper">
            <Sidebar activePath="/market" />
            <div className="main-content" style={{ padding: '60px 50px', backgroundColor: 'var(--bg-main)', minHeight: '100vh', fontFamily: "'Pretendard Variable', sans-serif" }}>
                
                {/* Header matches user mockup */}
                <div style={{ marginBottom: '40px' }}>
                    <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px', marginBottom: '16px' }}>
                        TERMINAL BENCHMARK :: REALFIFTY LEADING 50 COMPOSITE
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        {/* Left Side big number */}
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px' }}>
                            <span className="num-font" style={{ fontSize: '4rem', fontWeight: 900, color: '#fff', lineHeight: 1 }}>{latestRecovery.toFixed(2)}</span>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                <span className="num-font" style={{ fontSize: '1.2rem', color: diff >= 0 ? 'var(--color-cyan)' : 'var(--color-down)', fontWeight: 800 }}>
                                    {diff >= 0 ? '▲' : '▼'} {Math.abs(diff).toFixed(2)}p ({diffRate > 0 ? '+' : ''}{diffRate.toFixed(2)}%)
                                </span>
                                <span className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>PREV CLOSE: {prevRecovery.toFixed(2)}</span>
                            </div>
                        </div>

                        {/* Right side stats */}
                        <div style={{ display: 'flex', gap: '32px' }}>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>고점 대비 회복률</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-cyan)', lineHeight: 1 }}>
                                    {latestRecovery.toFixed(2)}%
                                </div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px' }}>전고점 100pt 기준</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>30일 누적 거래량</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: '#F87171', lineHeight: 1 }}>
                                    {latestVolume}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>건</span>
                                </div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '4px' }}>조건미달: -80.0%</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>시장 스트레스 지수</div>
                                <div className="num-font" style={{ fontSize: '2rem', fontWeight: 800, color: '#F87171', lineHeight: 1, display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                                    68 <span style={{ fontSize: '1rem', color: '#F87171' }}>위험 (HIGH)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Grid 1: Line Chart & Gauge */}
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: '20px', marginBottom: '20px' }}>
                    {/* Line Chart */}
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', fontWeight: 600 }}>
                                <span style={{ color: 'var(--color-cyan)' }}>✦</span> RealFifty 50 Leading Index Trajectory
                            </span>
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

                    {/* Gauges */}
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: '#fff' }}>실거래 회복률 분석 <span style={{ color: 'var(--text-muted)' }}>(CYCLE METRIC)</span></span>
                            <span style={{ color: 'var(--color-cyan)' }}>CYCLE METRIC</span>
                        </div>
                        
                        {/* Beautiful CSS ARC mockup */}
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
                            <svg width="200" height="100" viewBox="0 0 200 100">
                                {/* Background Arc */}
                                <path d="M 20 90 A 80 80 0 0 1 180 90" fill="none" stroke="#374151" strokeWidth="12" strokeLinecap="round" />
                                {/* Progress Arc */}
                                <path d="M 20 90 A 80 80 0 0 1 150 25" fill="none" stroke="var(--color-cyan)" strokeWidth="12" strokeLinecap="round" />
                                {/* Red Dot */}
                                <circle cx="150" cy="25" r="8" fill="#F87171" stroke="#111827" strokeWidth="3" />
                            </svg>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '-20px', marginBottom: '32px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            <span>저점 89.2%</span>
                            <span>현재 {latestRecovery.toFixed(2)}%</span>
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

                {/* Grid 2: Scatter Plot & Text + Volume */}
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: '20px' }}>
                    
                    {/* Scatter Plot */}
                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                        <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '24px', display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: '#fff', fontWeight: 600 }}>REALFIFTY MARKET MAP (4분면)</span>
                            <span style={{ padding: '4px 8px', border: '1px solid var(--border-light)', borderRadius: '4px', fontSize: '0.7rem' }}>DUAL-AXIS VALUATION RADAR</span>
                        </div>
                        <div style={{ height: '500px', position: 'relative' }}>
                            <div style={{ position: 'absolute', top: '10px', right: '40px', color: '#38BDF8', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT I: 신고가 랠리</div>
                            <div style={{ position: 'absolute', top: '10px', left: '40px', color: '#9CA3AF', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT II: 호가 방어 / 괴리 발생</div>
                            <div style={{ position: 'absolute', bottom: '20px', left: '40px', color: '#F87171', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT III: 과대 낙폭</div>
                            <div style={{ position: 'absolute', bottom: '20px', right: '40px', color: '#EAB308', fontSize: '0.75rem', fontWeight: 800, zIndex: 10 }}>QUADRANT IV: 급매 포착 구간</div>

                            <ResponsiveContainer width="100%" height="100%">
                                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                                    <CartesianGrid stroke="#374151" strokeDasharray="3 3" />
                                    <XAxis 
                                        type="number" 
                                        dataKey="mdd" 
                                        domain={[-35, 5]} 
                                        name="실거래 회복(MDD)" 
                                        stroke="var(--text-muted)" 
                                        fontSize={11}
                                        label={{ value: "◀ 실거래 하락 심각 (-35%)                      실거래 전고점 도달 (0%) ▶", position: "insideBottom", fill: "var(--text-muted)", fontSize: 10, dy: 15 }} 
                                    />
                                    <YAxis 
                                        type="number" 
                                        dataKey="gap" 
                                        domain={[-20, 30]} 
                                        name="호가 괴리율" 
                                        stroke="var(--text-muted)" 
                                        fontSize={11} 
                                    />
                                    <ZAxis type="number" range={[50, 50]} />
                                    <RechartsTooltip content={<ScatterTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                                    <ReferenceLine x={-15} stroke="#6B7280" strokeWidth={2} />
                                    <ReferenceLine y={0} stroke="#6B7280" strokeWidth={2} />
                                    
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

                    {/* Right column: Guidance + Volume */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        
                        {/* Guidance List */}
                        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                            <div className="num-font" style={{ fontSize: '0.85rem', color: '#fff', marginBottom: '20px', fontWeight: 600 }}>
                                <span style={{ color: '#38BDF8' }}>■</span> 4분면 매트릭스 리딩 가이던스
                            </div>
                            
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                <div>
                                    <div style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, marginBottom: '4px' }}>Q1. 주도주 / 과열 영역</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                                        전고점 대비 -15% 이내 회복 완료 및 매물 호가 강세 유지. 단기간 급반등한 단지 군집입니다. 추격 매수 시 강한 저항을 유의하십시오.
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, marginBottom: '4px' }}>Q2. 호가 방어 / 팽팽한 줄다리기</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                                        최근 실거래가는 -15% 이하로 크게 꺾였으나, 집주인들이 호가를 내리지 않는 '호가 방어력' 구간입니다. 매수/매도 호가 괴리가 깊어 거래절벽이 일어납니다.
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, marginBottom: '4px' }}>Q3. 과대 낙폭 / 바닥 탐색 구간</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                                        실거래와 호가 모두 -15% 이하로 붕괴했습니다. 시장 공포가 극에 달한 구간이나, 유동성 유입 시 가장 튀어오를 **턴어라운드/바닥 반등 후보** 입니다.
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, marginBottom: '4px' }}>Q4. 호가 조정 / 급매 포착 구간</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                                        실거래가는 버티고 있으나 최근 호가가 던져지고 있습니다. 단기적 모멘텀은 약하나 급매물(Bargain) 타겟팅이 가장 유리한 영역입니다.
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Volume Bar Chart */}
                        <div style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border-light)', padding: '24px' }}>
                            <div className="num-font" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                                <span style={{ color: '#fff', fontWeight: 600 }}>📊 50대 단지 거래량 유동성 고갈 추이</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                                (36-MONTH HISTORICAL VOLUME)
                            </div>
                            <div style={{ background: 'rgba(248, 113, 113, 0.1)', border: '1px solid var(--color-down)', padding: '12px', borderRadius: '4px', marginBottom: '24px' }}>
                                <div style={{ color: 'var(--color-down)', fontSize: '0.85rem', fontWeight: 800 }}>▲ 단 {latestVolume}건 체결로 유동성 증발.</div>
                            </div>
                            <div style={{ height: '180px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={volumeData}>
                                        <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={10} tickFormatter={(val) => val.replace('20', '')} interval={5} />
                                        <RechartsTooltip contentStyle={{ background: '#111827', border: '1px solid #374151', padding: '8px' }} />
                                        <Bar dataKey="volume" fill="#38BDF8" radius={[2, 2, 0, 0]} />
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
