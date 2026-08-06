"use client";
import React from 'react';

interface ComplexStat {
    complex: { name: string; id: string; gu: string };
    stats: any[];
}

export default function MacroGapRank({ kb50data }: { kb50data: ComplexStat[] }) {
    if (!kb50data || kb50data.length === 0) return null;

    const gapList = [];
    kb50data.forEach(c => {
        c.stats.forEach(s => {
            if (s.recent_deal_absolute && s.lowest_ask) {
                const rPrice = s.recent_deal_absolute.price;
                const aPrice = s.lowest_ask.price;
                if (rPrice > 0 && aPrice > 0) {
                    // Ask vs recent deal gap
                    const gapPct = ((aPrice - rPrice) / rPrice) * 100;
                    if (gapPct > 5) { // Only show where ask is at least 5% higher than recent deal
                        gapList.push({
                            c_name: c.complex.name,
                            type_name: s.pyeong_name,
                            recent_deal: rPrice,
                            lowest_ask: aPrice,
                            gap_pct: gapPct
                        });
                    }
                }
            }
        });
    });

    gapList.sort((a, b) => b.gap_pct - a.gap_pct);
    const top10 = gapList.slice(0, 10);

    const formatPrice = (v) => `${(v / 100000000).toFixed(1)}억`;

    return (
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>🔥 호가 vs 실거래 갭 (버티기 장세) TOP 10</h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>최근 실거래가 대비 현재 집주인이 제시하는 최저호가의 프리미엄 격차</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {top10.map((item, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', backgroundColor: '#f8fafc', borderRadius: '8px', borderLeft: i < 3 ? '4px solid #ef4444' : '4px solid #cbd5e1' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ fontWeight: 800, width: '24px', color: i < 3 ? '#ef4444' : '#94a3b8' }}>{i + 1}</div>
                            <div>
                                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#1e293b' }}>{item.c_name} <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 'normal' }}>{item.type_name}</span></div>
                                <div style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>실거래 <b>{formatPrice(item.recent_deal)}</b>  vs  호가 <b>{formatPrice(item.lowest_ask)}</b></div>
                            </div>
                        </div>
                        <div style={{ fontWeight: 800, color: '#ef4444', backgroundColor: '#fee2e2', padding: '6px 12px', borderRadius: '20px', fontSize: '0.95rem' }}>
                            +{item.gap_pct.toFixed(1)}%
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
