"use client";
import React, { useState } from 'react';
import {
    ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, ReferenceLine, Area
} from 'recharts';

interface TxData {
    month: string;
    recovery_rate: number;
    sample_count: number;
}

const RANGES = [
    { label: '1Y', months: 12 },
    { label: '3Y', months: 36 },
    { label: '5Y', months: 60 },
    { label: '전체', months: 9999 },
];

export default function MacroTxChart({ data }: { data: TxData[] }) {
    const [range, setRange] = useState(36);

    if (!data || data.length === 0) return null;

    const chartData = range === 9999 ? data : data.slice(-range);
    const latest = chartData[chartData.length - 1];
    const prev = chartData[chartData.length - 2];
    const diff = latest && prev ? (latest.recovery_rate - prev.recovery_rate).toFixed(2) : null;

    // Find ATH month (100%) and lowest month
    const minPoint = chartData.reduce((a, b) => a.recovery_rate < b.recovery_rate ? a : b);

    return (
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', marginBottom: '24px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>
                        📉 선도50 실거래가 회복률 추이
                    </h2>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>
                        50개 단지 국토부 실거래가 기준, 타입별 역대 최고가 대비 체결률 중앙값
                    </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '2px' }}>최근 체결 회복률</div>
                    <div style={{ fontSize: '2rem', fontWeight: 900, color: latest?.recovery_rate >= 95 ? '#10b981' : latest?.recovery_rate >= 80 ? '#f59e0b' : '#ef4444' }}>
                        {latest?.recovery_rate}%
                    </div>
                    {diff && (
                        <div style={{ fontSize: '0.85rem', color: parseFloat(diff) >= 0 ? '#10b981' : '#ef4444', fontWeight: 700 }}>
                            {parseFloat(diff) >= 0 ? '▲' : '▼'} {Math.abs(parseFloat(diff))}p (전월비)
                        </div>
                    )}
                </div>
            </div>

            {/* Range selector */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                {RANGES.map(r => (
                    <button
                        key={r.label}
                        onClick={() => setRange(r.months)}
                        style={{
                            padding: '4px 12px',
                            borderRadius: '6px',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '0.85rem',
                            fontWeight: range === r.months ? 800 : 500,
                            backgroundColor: range === r.months ? '#1e293b' : '#f1f5f9',
                            color: range === r.months ? 'white' : '#64748b',
                            transition: 'all 0.15s',
                        }}
                    >
                        {r.label}
                    </button>
                ))}
                <div style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#94a3b8', alignSelf: 'center' }}>
                    {chartData.length}개월 ({chartData[0]?.month} ~ {latest?.month})
                </div>
            </div>

            {/* Chart */}
            <div style={{ width: '100%', height: 280 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis
                            dataKey="month"
                            tick={{ fill: '#888', fontSize: 11 }}
                            tickFormatter={(tick) => tick.substring(2)}
                            axisLine={false}
                            tickLine={false}
                            minTickGap={range <= 12 ? 10 : range <= 36 ? 20 : 40}
                        />
                        <YAxis
                            domain={['auto', 105]}
                            tick={{ fill: '#888', fontSize: 12 }}
                            tickFormatter={(tick) => `${tick}%`}
                            axisLine={false}
                            tickLine={false}
                            width={48}
                        />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.12)', fontSize: '0.9rem' }}
                            formatter={(value: any, name: any, props: any) => [
                                `${value}% (${props?.payload?.sample_count}건 기준)`,
                                '역대최고가 대비 체결률'
                            ]}
                            labelFormatter={(label) => `${label}`}
                            cursor={{ stroke: '#e2e8f0', strokeWidth: 2 }}
                        />
                        {/* ATH reference line at 100% */}
                        <ReferenceLine
                            y={100}
                            stroke="#1e293b"
                            strokeDasharray="5 5"
                            strokeOpacity={0.4}
                            label={{ position: 'insideTopRight', value: '역대최고가 (100%)', fill: '#1e293b', fontSize: 10 }}
                        />
                        <Area
                            type="monotone"
                            dataKey="recovery_rate"
                            fill="url(#areaGrad)"
                            stroke="none"
                        />
                        <Line
                            type="monotone"
                            dataKey="recovery_rate"
                            stroke="#3b82f6"
                            strokeWidth={2.5}
                            dot={range <= 12 ? { r: 4, fill: '#3b82f6', strokeWidth: 0 } : false}
                            activeDot={{ r: 6, fill: '#3b82f6', strokeWidth: 0 }}
                        />
                    </ComposedChart>
                </ResponsiveContainer>
            </div>

            {/* Info footer */}
            <div style={{ display: 'flex', gap: '24px', marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #f1f5f9' }}>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    <span style={{ fontWeight: 700, color: '#ef4444' }}>저점</span>{' '}
                    {minPoint.month} ({minPoint.recovery_rate}%)
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    <span style={{ fontWeight: 700, color: '#10b981' }}>현재</span>{' '}
                    {latest?.month} ({latest?.recovery_rate}%)
                </div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: 'auto' }}>
                    * 국토부 실거래 신고 기준, 50개 단지 타입별 중앙값
                </div>
            </div>
        </div>
    );
}
