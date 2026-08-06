"use client";
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';

interface VolumeData {
    month: string;
    trade_count: number;
    volume_ratio: number;
}

export default function MacroVolumeChart({ data, ath_count }: { data: VolumeData[], ath_count: number }) {
    if (!data || data.length === 0) return null;

    // Show only last 18 months to avoid chart overcrowding
    const chartData = data.slice(-18);
    // Current month (last item) is partial - mark it
    const currentMonthStr = new Date().toISOString().substring(0, 7);
    const prevMonth = chartData[chartData.length - 2]; // last complete month

    return (
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', marginBottom: '24px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>🌊 역대 최대치 대비 월간 거래량 추이</h2>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: '0 0 4px 0' }}>
                        2017년 5월 폭등장 최성기({ath_count.toLocaleString()}건) 대비 현재 시장의 매수 유동성
                    </p>
                    <p style={{ fontSize: '0.8rem', color: '#f59e0b', margin: 0 }}>
                        ⚠️ 국토부 신고기한(30일) 특성상 최근 1~2개월 수치는 집계 진행 중입니다
                    </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '2px' }}>전월 확정 거래</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#3b82f6' }}>
                        {prevMonth?.volume_ratio ?? 0}%
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
                        {prevMonth?.trade_count?.toLocaleString() ?? 0}건
                    </div>
                </div>
            </div>

            <div style={{ width: '100%', height: 240 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis
                            dataKey="month"
                            tick={{ fill: '#888', fontSize: 11 }}
                            tickFormatter={(tick) => tick.substring(2)}
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
                            formatter={(value: any, name: any, props: any) => {
                                const isCurrentMonth = props?.payload?.month === currentMonthStr;
                                return [`${value}% (${props?.payload?.trade_count}건)${isCurrentMonth ? ' ⚠️집계중' : ''}`, '역대 최대 대비'];
                            }}
                            labelFormatter={(label) => `${label}`}
                            cursor={{ fill: '#f1f5f9' }}
                        />
                        <ReferenceLine y={100} stroke="#3b82f6" strokeDasharray="4 4" strokeOpacity={0.4} label={{ position: 'insideTopRight', value: '역대최대(100%)', fill: '#3b82f6', fontSize: 10 }} />
                        <Bar dataKey="volume_ratio" radius={[4, 4, 0, 0]} animationDuration={1200} barSize={28}>
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={entry.month === currentMonthStr ? '#fbbf24' : entry.volume_ratio > 20 ? '#60a5fa' : '#93c5fd'}
                                    opacity={entry.month === currentMonthStr ? 0.6 : 1}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8', textAlign: 'right', marginTop: '4px' }}>
                * 노란 막대 = 이번달 (집계 진행 중)
            </div>
        </div>
    );
}
