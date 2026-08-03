"use client";

import React, { useState, useMemo, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import rawData from '@/data/kb50_stats.json';
import TickerClient from '../../TickerClient';
import '@/app/globals.css';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart } from 'recharts';

function formatPriceNum(num: number) {
    if (!num) return '-';
    const eok = Math.floor(num / 100000000);
    const man = Math.floor((num % 100000000) / 10000);
    const manStr = man > 0 ? `.${Math.floor(man / 1000)}` : '';
    return `${eok}${manStr}`;
}

function formatDate(dateStr: string) {
    if (!dateStr) return '';
    return dateStr.replace('202', '2').replace(/-/g, '.');
}

function getRepIndex(stats: any[]) {
    if (!stats || stats.length === 0) return 0;
    const now = new Date().getTime();
    const scoredStats = stats.map((s: any, idx: number) => {
        let diffDays = 99999;
        if (s.recent_deal_absolute && s.recent_deal_absolute.date) {
            const lastDate = new Date(s.recent_deal_absolute.date).getTime();
            diffDays = Math.abs(now - lastDate) / (1000 * 3600 * 24);
        }
        const dist84 = Math.abs(s.match_key_area - 84);
        const isAlive = diffDays <= 365;
        const groupDist = (s.match_key_area >= 82 && s.match_key_area <= 85) ? 0 : dist84;
        return { ...s, diffDays, dist84, isAlive, groupDist, originalIdx: idx };
    });
    scoredStats.sort((a, b) => {
        if (a.isAlive !== b.isAlive) return a.isAlive ? -1 : 1;
        if (a.groupDist !== b.groupDist) return a.groupDist - b.groupDist;
        return b.highest_deal_price - a.highest_deal_price;
    });
    return scoredStats[0].originalIdx;
}

function getRepresentativeStat(stats: any[]) {
    if (!stats || stats.length === 0) return null;
    const now = new Date().getTime();

    const scoredStats = stats.map((s: any) => {
        let diffDays = 99999;
        if (s.recent_deal_absolute && s.recent_deal_absolute.date) {
            const lastDate = new Date(s.recent_deal_absolute.date).getTime();
            diffDays = Math.abs(now - lastDate) / (1000 * 3600 * 24);
        }
        const dist84 = Math.abs(s.match_key_area - 84);
        const isAlive = diffDays <= 365;
        const groupDist = (s.match_key_area >= 82 && s.match_key_area <= 85) ? 0 : dist84;

        return { ...s, diffDays, dist84, isAlive, groupDist };
    });

    scoredStats.sort((a, b) => {
        if (a.isAlive !== b.isAlive) return a.isAlive ? -1 : 1;
        if (a.groupDist !== b.groupDist) return a.groupDist - b.groupDist;
        return b.highest_deal_price - a.highest_deal_price;
    });

    return scoredStats[0];
}

export default function DetailPage() {
    const params = useParams();
    const router = useRouter();
    const complexId = params.id as string;

    const group = (rawData as any[]).find(g => g.complex.id === complexId);

    const sortedStats = group ? [...group.stats].map(s => {
        const mdd_rate = s.highest_deal_price > 0 ? -Math.abs(((s.highest_deal_price - s.current_lowest_ask) / s.highest_deal_price) * 100) : 0;
        return { ...s, mdd_rate };
    }).sort((a, b) => {
        if (a.match_key_area !== b.match_key_area) return a.match_key_area - b.match_key_area;
        return (a.pyeong_name || "").localeCompare(b.pyeong_name || "");
    }) : [];

    const [activeIndex, setActiveIndex] = useState(() => getRepIndex(sortedStats));
    const [chartPeriod, setChartPeriod] = useState<1 | 5 | 10>(10);
    const [chartType, setChartType] = useState<'price' | 'volume' | 'ask'>('price');
    const [chartDataState, setChartDataState] = useState<any>(null);

    const complexIdStr = Array.isArray(complexId) ? complexId[0] : complexId;

    useEffect(() => {
        if (!complexIdStr) return;
        fetch(`/chart_data/${complexIdStr}.json`)
            .then(res => res.json())
            .then(data => setChartDataState(data))
            .catch(err => console.error("차트 데이터를 쿼리하는데 실패했습니다.", err));
    }, [complexIdStr]);

    if (!group) return <div style={{ padding: '50px' }}>단지를 찾을 수 없습니다.</div>;
    const complex = group.complex;

    const activeStat = sortedStats[activeIndex];
    const ath = activeStat.highest_deal_price;
    const absoluteRecent = activeStat.recent_deal_absolute;
    const currentAsk = activeStat.current_lowest_ask;
    const mddStr = activeStat.mdd_rate ? Math.abs(activeStat.mdd_rate).toFixed(1) : '0.0';

    const monthDealsCount = activeStat.month_volume || 0;
    const volumeDropRate = activeStat.volume_drop_rate || 0;

    const absDrop = absoluteRecent ? (((ath - absoluteRecent.price) / ath) * 100).toFixed(1) : '0.0';
    const txList = activeStat.month_deals || [];

    const currentMonth = new Date().getMonth() + 1;

    const currentArea = activeStat?.match_key_area;

    const miniVolumeData = useMemo(() => {
        if (!chartDataState || !currentArea || !chartDataState[currentArea]) return [];
        const volume = chartDataState[currentArea].volume || [];
        const now = new Date();
        const past = new Date(now.getFullYear(), now.getMonth() - 11, 1);
        const limitTimestamp = past.getTime();

        const res: any[] = [];
        volume.forEach((v: any) => {
            const time = new Date(v.month + "-15").getTime();
            if (time >= limitTimestamp) {
                const monthNum = new Date(time).getMonth() + 1;
                res.push({ name: `${monthNum}월`, count: v.count });
            }
        });

        const filled = [];
        for (let i = 11; i >= 0; i--) {
            const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
            const label = `${d.getMonth() + 1}월`;
            const found = res.find(r => r.name === label);
            filled.push({ name: label, count: found ? found.count : 0 });
        }
        return filled;
    }, [chartDataState, currentArea]);

    const chartData = useMemo(() => {
        if (!chartDataState || !currentArea || !chartDataState[currentArea]) return [];

        const areaData = chartDataState[currentArea];
        const trades = areaData.trades || [];
        const volume = areaData.volume || [];
        const asks = areaData.asks || [];

        const now = new Date();
        const startTime = new Date();
        startTime.setFullYear(now.getFullYear() - chartPeriod);
        const startTimestamp = startTime.getTime();

        const points: any[] = [];

        trades.forEach((t: any) => {
            const time = new Date(t.date).getTime();
            if (time >= startTimestamp) {
                points.push({ time, dealPrice: parseFloat((t.price / 100000000).toFixed(2)) });
            }
        });

        asks.forEach((a: any) => {
            const time = new Date(a.date).getTime();
            if (time >= startTimestamp) {
                points.push({ time, askPrice: parseFloat((a.price / 100000000).toFixed(2)) });
            }
        });

        volume.forEach((v: any) => {
            const time = new Date(v.month + "-15").getTime();
            if (time >= startTimestamp) {
                points.push({ time, volumeCount: v.count });
            }
        });

        points.sort((a, b) => a.time - b.time);

        return points;
    }, [chartDataState, currentArea, chartPeriod]);

    let diffDays = 0;
    let lastDealDateStr = '-';
    if (absoluteRecent && absoluteRecent.date) {
        const lastDate = new Date(absoluteRecent.date);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - lastDate.getTime());
        diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        const yy = absoluteRecent.date.substring(2, 4);
        const mm = absoluteRecent.date.substring(5, 7);
        const dd = absoluteRecent.date.substring(8, 10);
        lastDealDateStr = `${yy}.${mm}.${dd}`;
    }

    return (
        <div className="app-wrapper">
            <aside className="sidebar">
                <div className="sidebar-logo" style={{ padding: '32px 24px 12px 24px' }}>
                    <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                        Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
                    </div>

                </div>
                <div className="sidebar-menu" style={{ marginTop: '20px' }}>
                    <div className="menu-item" onClick={() => router.push('/')}>📊 실시간 시장 현황 (메인)</div>
                    <div className="menu-item active">📊 통합 마켓 상세 현황</div>
                    <div className="menu-item">🔔 가격 변동 알림 (준비중)</div>
                    <div className="menu-item">💼 관심 단지 등록 (준비중)</div>
                </div>
            </aside>

            <div className="main-content" style={{ backgroundColor: '#f7f9fc' }}>
                <div className="top-ticker" style={{ padding: 0, overflow: 'hidden' }}>
                    <TickerClient items={(() => {
                        const totalDropRates = (rawData as any[]).map(g => {
                            const rep = getRepresentativeStat(g.stats);
                            return rep ? rep.recent_drop_rate : 0;
                        }).filter(d => d < 0);
                        const avgNum = totalDropRates.length > 0
                            ? parseFloat((totalDropRates.reduce((acc, val) => acc + val, 0) / totalDropRates.length).toFixed(2))
                            : 0;

                        const groupedDataForTicker: any[] = [...(rawData as any[])].map(g => {
                            const rep = getRepresentativeStat(g.stats);
                            return {
                                name: g.complex.name,
                                recent_drop_rate: rep ? rep.recent_drop_rate : 0
                            };
                        }).sort((a, b) => a.recent_drop_rate - b.recent_drop_rate);

                        groupedDataForTicker.forEach((g, idx) => g.rank = idx + 1);

                        return groupedDataForTicker
                            .filter(item => item.recent_drop_rate < avgNum)
                            .map(item => ({
                                name: item.name,
                                drop: item.recent_drop_rate.toFixed(1),
                                isSevere: item.recent_drop_rate <= -20,
                                rank: item.rank
                            }));
                    })()} />
                </div>

                <div className="dashboard-area" style={{ padding: '24px 40px' }}>

                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
                        <button onClick={() => router.push('/')} style={{ border: 'none', background: '#e0e3e6', color: '#191c1e', width: '40px', height: '40px', borderRadius: '8px', cursor: 'pointer', marginRight: '16px', fontWeight: 'bold' }}>←</button>
                        <div>
                            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#191c1e' }}>{complex.name}</h1>
                            <div style={{ fontSize: '0.9rem', color: '#76777d', marginTop: '4px' }}>📍 {complex.region}</div>
                        </div>
                        <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
                        </div>
                    </div>

                    <div style={{ background: '#131b2e', borderRadius: '12px', padding: '20px', marginBottom: '24px' }}>
                        <div style={{ color: 'white', fontSize: '0.85rem', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M4 4h16v16H4V4zm2 2v12h12V6H6z" /></svg>
                            단지 내 전용면적별 분석 (㎡)
                        </div>
                        <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', paddingBottom: '8px' }}>
                            {sortedStats.map((s, idx) => {
                                const isActive = idx === activeIndex;
                                return (
                                    <div
                                        key={idx}
                                        onClick={() => setActiveIndex(idx)}
                                        style={{
                                            minWidth: '80px', height: '80px', flexShrink: 0,
                                            background: isActive ? '#ffffff' : '#1e293b',
                                            color: isActive ? '#131b2e' : '#ffffff',
                                            border: isActive ? '2px solid #ba1a1a' : '1px solid rgba(255,255,255,0.1)',
                                            borderRadius: '8px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                                            cursor: 'pointer', transition: 'all 0.2s', fontWeight: 700
                                        }}
                                    >
                                        {s.pyeong_name && (
                                            <span style={{ fontSize: '1rem', fontWeight: 900, opacity: isActive ? 1 : 0.7, marginBottom: '2px', color: isActive ? '#ba1a1a' : '#fff' }}>
                                                {s.pyeong_name.includes('㎡') || s.pyeong_name.includes('형') ? s.pyeong_name : `${s.pyeong_name}형`}
                                            </span>
                                        )}
                                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '3px' }}>
                                            <span style={{ fontSize: '0.8rem', opacity: isActive ? 0.9 : 0.6, fontWeight: 600 }}>전용</span>
                                            <span className="num-font" style={{ fontSize: '1.4rem' }}>{s.match_key_area}</span>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '24px' }}>

                        <div className="ap-card" style={{ padding: '24px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#76777d', fontSize: '0.85rem', fontWeight: 600, marginBottom: '16px' }}>
                                <span>최고가 및 실거래 낙폭 분석</span>
                                <span>📉</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#191c1e', fontWeight: 700 }}>역대 최고가 <span className="num-font">({formatDate(activeStat.highest_deal_date)})</span></div>
                            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '20px' }}>
                                <span className="num-font">{formatPriceNum(ath)}</span><span className="kr-unit">억</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#191c1e', fontWeight: 700 }}>
                                가장 최근 체결된 실거래가 <span className="num-font" style={{ color: '#ba1a1a', opacity: 0.8, marginLeft: '6px' }}>({lastDealDateStr})</span>
                            </div>
                            <div style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '20px' }}>
                                {absoluteRecent ? <><span className="num-font">{formatPriceNum(absoluteRecent.price)}</span><span className="kr-unit">억</span></> : '-'}
                            </div>
                            <div style={{ background: '#ffdad6', color: '#93000b', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderRadius: '6px', fontWeight: 800, fontSize: '1.2rem' }}>
                                <span className="num-font">{-absDrop}%</span>
                                <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>고점 대비 수익률 하락</span>
                            </div>
                        </div>

                        <div className="ap-card" style={{ padding: '24px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#76777d', fontSize: '0.85rem', fontWeight: 600, marginBottom: '16px' }}>
                                <span>시장 매수 유동성 분석</span>
                                <span>📊</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#191c1e', fontWeight: 700 }}>당월 ({currentMonth}월) 실질 매수 체결량</div>
                            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '16px' }}>
                                <span className="num-font">{monthDealsCount}</span> <span className="kr-unit">건</span>
                            </div>

                            <div style={{ height: '70px', width: '100%', position: 'relative', borderBottom: '2px solid #e0e3e6', marginTop: 'auto' }}>
                                <ResponsiveContainer width="100%" height="85%">
                                    <BarChart data={miniVolumeData}>
                                        <Bar dataKey="count" fill="#4ade80" radius={[2, 2, 0, 0]} />
                                        <RechartsTooltip cursor={{ fill: '#f2f4f7' }} contentStyle={{ fontSize: '0.8rem', padding: '4px 8px', borderRadius: '4px', border: 'none', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }} formatter={(val: any) => [`${val}건`, '거래량']} labelStyle={{ display: 'none' }} />
                                    </BarChart>
                                </ResponsiveContainer>
                                <div style={{ position: 'absolute', bottom: '-22px', right: '0', fontSize: '0.7rem', color: '#76777d', fontWeight: 600 }}>최근 12개월 월별 거래량</div>
                            </div>

                        </div>

                        <div className="ap-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#76777d', fontSize: '0.85rem', fontWeight: 600, marginBottom: '16px' }}>
                                <span>실시간 시장 매물(호가) 현황</span>
                                <span>🏷️</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#191c1e', fontWeight: 700 }}>최저호가</div>
                            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '20px' }}>
                                <span className="num-font">{formatPriceNum(currentAsk)}</span><span className="kr-unit">억</span>
                            </div>

                            <div style={{ fontSize: '1rem', color: '#131b2e', fontWeight: 800, marginBottom: '20px', minHeight: '38px', paddingTop: '4px', letterSpacing: '-0.5px' }}>
                                {(() => {
                                    const gap = currentAsk - (absoluteRecent ? absoluteRecent.price : 0);
                                    if (!absoluteRecent) return '최근 실거래 없음';
                                    const gapEok = Math.abs(gap / 100000000).toFixed(1);
                                    if (gap < 0) return `↓ 최근 실거래가 대비 ${gapEok}억원 저렴`;
                                    if (gap > 0) return `↑ 최근 실거래가 대비 ${gapEok}억원 비쌈`;
                                    return `- 최근 실거래가와 동일`;
                                })()}
                            </div>

                            <div style={{ marginTop: 'auto', background: (activeStat.mdd_rate ?? 0) <= 0 ? '#dae2fd' : '#ffdad6', color: (activeStat.mdd_rate ?? 0) <= 0 ? '#131b2e' : '#93000b', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '12px 16px', borderRadius: '6px', fontWeight: 800, fontSize: '1.05rem', letterSpacing: '-0.5px' }}>
                                최고가 대비 <span className="num-font" style={{ margin: '0 6px', fontSize: '1.2rem' }}>{mddStr}%</span> {(activeStat.mdd_rate ?? 0) <= 0 ? '저렴' : '비쌈'}
                            </div>
                        </div>

                    </div>

                    <div className="ap-card" style={{ padding: '30px', marginBottom: '24px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>📊 장기 분석 궤적</h2>
                                <div style={{ display: 'flex', gap: '6px' }}>
                                    {[
                                        { id: 'price', label: '실거래가' },
                                        { id: 'volume', label: '거래량' },
                                        { id: 'ask', label: '최저호가' }
                                    ].map(tab => (
                                        <button
                                            key={tab.id}
                                            onClick={() => setChartType(tab.id as any)}
                                            style={{
                                                border: 'none',
                                                background: chartType === tab.id ? '#131b2e' : '#f2f4f7',
                                                color: chartType === tab.id ? 'white' : '#76777d',
                                                padding: '6px 14px', fontSize: '0.85rem', borderRadius: '20px',
                                                cursor: 'pointer', fontWeight: 700,
                                                transition: 'all 0.2s',
                                                boxShadow: chartType === tab.id ? '0 2px 8px rgba(0,0,0,0.1)' : 'none'
                                            }}
                                        >
                                            {tab.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                {[10, 5, 1].map((p) => (
                                    <span
                                        key={p}
                                        onClick={() => setChartPeriod(p as 1 | 5 | 10)}
                                        style={{
                                            background: chartPeriod === p ? '#191c1e' : '#e0e3e6',
                                            color: chartPeriod === p ? 'white' : '#191c1e',
                                            padding: '6px 14px', fontSize: '0.85rem', borderRadius: '6px',
                                            cursor: 'pointer', fontWeight: 700,
                                            transition: 'all 0.2s',
                                            boxShadow: chartPeriod === p ? '0 2px 8px rgba(0,0,0,0.2)' : 'none'
                                        }}
                                    >
                                        {p}년
                                    </span>
                                ))}
                            </div>
                        </div>
                        <div style={{ width: '100%', height: '400px', position: 'relative', overflow: 'hidden' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={chartData} margin={{ top: 30, right: 30, left: 10, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e0e3e6" />
                                    <XAxis
                                        dataKey="time"
                                        type="number"
                                        domain={['dataMin', 'dataMax']}
                                        scale="time"
                                        tickFormatter={(time) => {
                                            const d = new Date(time);
                                            return `${d.getFullYear().toString().slice(2)}년`;
                                        }}
                                        tick={{ fontSize: 13, fill: '#76777d' }}
                                        axisLine={false}
                                        tickLine={false}
                                        minTickGap={30}
                                    />
                                    <YAxis
                                        domain={chartType === 'volume' ? [0, (dataMax: number) => dataMax === 0 ? 10 : Math.ceil(dataMax * 1.5)] : ['auto', 'auto']}
                                        tick={{ fontSize: 13, fill: '#76777d', fontWeight: 600 }}
                                        tickFormatter={(v) => chartType === 'volume' ? `${v}건` : `${v}억`}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    <RechartsTooltip
                                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', fontWeight: 700 }}
                                        labelStyle={{ color: '#131b2e', fontSize: '0.9rem', marginBottom: '6px' }}
                                        labelFormatter={(value) => {
                                            const d = new Date(value as number);
                                            return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;
                                        }}
                                        formatter={(value: any, name: any) => {
                                            if (name === 'dealPrice') return [`${value}억`, '실거래가'];
                                            if (name === 'askPrice') return [`${value}억`, '네이버 최저호가'];
                                            if (name === 'volumeCount') return [`${value}건`, '월간 거래량'];
                                            return [value, name];
                                        }}
                                    />
                                    {chartType === 'volume' && <Bar dataKey="volumeCount" fill="#f87171" barSize={16} opacity={0.9} radius={[4, 4, 0, 0]} />}
                                    {chartType === 'ask' && <Line connectNulls type="linear" dataKey="askPrice" stroke="#f97316" strokeWidth={2} dot={{ r: 2.5, fill: '#f97316' }} activeDot={{ r: 6 }} />}
                                    {chartType === 'price' && <Line connectNulls type="linear" dataKey="dealPrice" stroke="#60a5fa" strokeWidth={2.5} dot={{ r: 3, fill: '#3b82f6' }} activeDot={{ r: 7 }} />}
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>
                        <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.85rem', color: '#76777d' }}>* 과거 {chartPeriod}년간의 {chartType === 'price' ? '실거래가' : (chartType === 'volume' ? '월간 거래량' : '네이버 최저호가')} 변화 추이입니다.</div>
                    </div>

                    <div className="ap-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '24px', borderBottom: '1px solid #e0e3e6' }}>
                            <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>📋 당월 ({currentMonth}월) 확정 실거래 내역</h2>
                        </div>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: '0.95rem' }}>
                            <thead style={{ background: '#f2f4f7', color: '#76777d', fontSize: '0.8rem' }}>
                                <tr>
                                    <th style={{ padding: '16px' }}>체결 일자</th>
                                    <th style={{ padding: '16px' }}>거래 금액 (억원)</th>
                                    <th style={{ padding: '16px' }}>면적 / 층</th>
                                    <th style={{ padding: '16px' }}>거래 유형</th>
                                </tr>
                            </thead>
                            <tbody>
                                {txList.map((tx: any, i: number) => (
                                    <tr key={i} style={{ borderBottom: '1px solid #e0e3e6', transition: 'background 0.2s', cursor: 'pointer' }}>
                                        <td className="num-font" style={{ padding: '20px 16px', fontWeight: 700 }}>{tx.date?.slice(0, 10)}</td>
                                        <td style={{ padding: '20px 16px', fontSize: '1.1rem', fontWeight: 800 }}><span className="num-font">{(tx.price / 100000000).toFixed(1)}</span><span className="kr-unit">억</span></td>
                                        <td style={{ padding: '20px 16px', color: '#45464d' }}>
                                            <span style={{ fontWeight: 700, color: '#131b2e', marginRight: '6px' }}>{activeStat.pyeong_name}</span>
                                            <span className="num-font">{activeStat.match_key_area}</span>m² / <span className="num-font">{tx.floor || '-'}</span>층
                                        </td>
                                        <td style={{ padding: '20px 16px', color: '#76777d' }}>{tx.type || '중개거래'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {txList.length === 0 && (
                            <div style={{ padding: '50px', textAlign: 'center', color: '#76777d', fontSize: '1rem', borderBottom: '1px solid #e0e3e6' }}>
                                이전 거래일(<span className="num-font">{lastDealDateStr}</span>) 이후로
                                <div className="freeze-warning" style={{ fontSize: '1.5rem', marginTop: '12px' }}>
                                    <span className="num-font">{diffDays}</span>일간 거래 없음
                                </div>
                            </div>
                        )}
                        <div style={{ padding: '20px', textAlign: 'center', color: '#ba1a1a', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', background: '#f7f9fc' }}>10년치(약 150개월) 거래 원장 조회기능 준비중</div>
                    </div>

                </div>
            </div>
        </div>
    );
}
// trigger HMR
