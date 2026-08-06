"use client";
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface VolumeData {
    month: string;
    trade_count: number;
    volume_ratio: number;
}

export default function MacroVolumeChart({ data, ath_count }: { data: VolumeData[], ath_count: number }) {
    if (!data || data.length === 0) return null;

    // Highlight current month vs previous
    const currentMonth = data[data.length - 1];

    return (
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', marginBottom: '24px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                <div>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>🌊 역대 최대치 대비 월간 거래량 추이</h2>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>과거 폭등장 최다 거래량 월({ath_count}건) 대비 현재 시장의 매수 유동성 분석</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#3b82f6' }}>
                        {currentMonth.volume_ratio}%
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 'bold', color: '#64748b' }}>
                        이번달 거래 체결 {currentMonth.trade_count}건
                    </div>
                </div>
            </div>

            <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis
                            dataKey="month"
                            tick={{ fill: '#888', fontSize: 11 }}
                            tickFormatter={(tick) => tick.substring(2)} // Show YY-MM
                            axisLine={false}
                            tickLine={false}
                            minTickGap={20}
                        />
                        <YAxis
                            domain={[0, 100]}
                            tick={{ fill: '#888', fontSize: 12 }}
                            tickFormatter={(tick) => `${tick}%`}
                            axisLine={false}
                            tickLine={false}
                            width={45}
                        />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                            formatter={(value: any) => [`${value}%`, '가뭄 지수 (역대 최대 대비)']}
                            labelFormatter={(label) => `📅 ${label}`}
                            cursor={{ fill: '#f1f5f9' }}
                        />
                        <ReferenceLine y={100} stroke="#3b82f6" strokeDasharray="3 3" strokeOpacity={0.3} label={{ position: 'top', value: '역대 최대 유동성 (100%)', fill: '#3b82f6', fontSize: 11 }} />
                        <Bar
                            dataKey="volume_ratio"
                            fill="#60a5fa"
                            radius={[4, 4, 0, 0]}
                            animationDuration={1500}
                            barSize={30}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
