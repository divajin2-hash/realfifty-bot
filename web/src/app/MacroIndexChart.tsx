"use client";
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface MacroData {
    date: string;
    market_recovery_index: number;
}

export default function MacroIndexChart({ data }: { data: MacroData[] }) {
    if (!data || data.length === 0) return null;

    // Get min and max for dynamic scaling
    const minRaw = Math.min(...data.map(d => d.market_recovery_index));
    const maxRaw = Math.max(...data.map(d => d.market_recovery_index));
    const minDomain = Math.floor(minRaw - 1);
    const maxDomain = Math.ceil(maxRaw + 1);

    const latestIndex = data[data.length - 1].market_recovery_index;
    const prevIndex = data.length > 1 ? data[data.length - 2].market_recovery_index : latestIndex;
    const diff = (latestIndex - prevIndex).toFixed(2);
    const isUp = latestIndex >= prevIndex;

    return (
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', marginBottom: '24px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                <div>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>📈 RealFifty 고유 거시 인덱스</h2>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>서울 50대장 전체 단지의 <b>전고점 대비 현재 호가 회복률(%)</b> 추이</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.8rem', fontWeight: 900, color: isUp ? '#d24f45' : '#1261c4' }}>
                        {latestIndex}%
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 'bold', color: isUp ? '#d24f45' : '#1261c4' }}>
                        {isUp ? '▲' : '▼'} {Math.abs(Number(diff))}p (전일 대비)
                    </div>
                </div>
            </div>

            <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis
                            dataKey="date"
                            tick={{ fill: '#888', fontSize: 12 }}
                            tickFormatter={(tick) => tick.substring(5)} // Show MM-DD
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            domain={[minDomain, maxDomain]}
                            tick={{ fill: '#888', fontSize: 12 }}
                            tickFormatter={(tick) => `${tick}%`}
                            axisLine={false}
                            tickLine={false}
                            width={45}
                        />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                            formatter={(value: any) => [`${value}%`, '시장 회복률']}
                            labelFormatter={(label) => `📅 ${label}`}
                        />
                        <ReferenceLine y={100} stroke="#ff0000" strokeDasharray="3 3" strokeOpacity={0.3} label={{ position: 'top', value: '전고점 (100%)', fill: '#ff0000', fontSize: 11 }} />
                        <Line
                            type="monotone"
                            dataKey="market_recovery_index"
                            stroke="#d24f45"
                            strokeWidth={3}
                            dot={{ r: 4, strokeWidth: 2, fill: 'white' }}
                            activeDot={{ r: 6, strokeWidth: 0 }}
                            animationDuration={1500}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
