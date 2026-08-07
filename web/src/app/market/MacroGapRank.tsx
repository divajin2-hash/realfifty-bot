"use client";
import React from 'react';

interface ComplexStat {
    complex: { name: string; id: string; gu: string };
    stats: any[];
}

export default function MacroGapRank({ kb50data }: { kb50data: ComplexStat[] }) {
    if (!kb50data || kb50data.length === 0) return null;

    const gapList: any[] = [];

    // Only consider deals within the last 180 days for a true "standoff" indicator
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 180);
    const cutoffStr = cutoffDate.toISOString().substring(0, 10);

    kb50data.forEach(c => {
        // 동일 단지 내 쌍둥이 평형(같은 전용면적) 중 대표 1개만 추출
        const representativeStats = new Map<number, any>();

        c.stats.forEach(s => {
            const currentArea = s.match_key_area;
            const existing = representativeStats.get(currentArea);

            if (!existing) {
                representativeStats.set(currentArea, s);
            } else {
                // 더 적합한 대표 평형(volume, 'A' 우선, ATH)으로 교체
                const eVol = existing.month_volume || 0;
                const cVol = s.month_volume || 0;
                const eIsA = existing.pyeong_name?.includes('A') ? 1 : 0;
                const cIsA = s.pyeong_name?.includes('A') ? 1 : 0;
                const eAth = existing.highest_deal_price || 0;
                const cAth = s.highest_deal_price || 0;

                if (cVol > eVol) {
                    representativeStats.set(currentArea, s);
                } else if (cVol === eVol && cIsA > eIsA) {
                    representativeStats.set(currentArea, s);
                } else if (cVol === eVol && cIsA === eIsA && cAth > eAth) {
                    representativeStats.set(currentArea, s);
                }
            }
        });

        // 엄선된 대표 평형만 랭킹에 참여
        representativeStats.forEach(s => {
            const rPrice = s.recent_deal_absolute?.price;
            const rDate = s.recent_deal_absolute?.date;
            const aPrice = s.current_lowest_ask;

            // Validate and enforce the recency cutoff
            if (rPrice && aPrice && rPrice > 0 && aPrice > 0 && rDate && rDate >= cutoffStr) {
                const gapPct = ((aPrice - rPrice) / rPrice) * 100;
                gapList.push({
                    c_name: c.complex.name,
                    type_name: s.pyeong_name,
                    recent_deal: rPrice,
                    deal_date: rDate.substring(2), // YY-MM-DD
                    lowest_ask: aPrice,
                    gap_pct: gapPct
                });
            }
        });
    });

    const highList = gapList.filter(g => g.gap_pct > 2).sort((a, b) => b.gap_pct - a.gap_pct).slice(0, 10);
    const lowList = gapList.filter(g => g.gap_pct < -0.1).sort((a, b) => a.gap_pct - b.gap_pct).slice(0, 10);

    const formatPrice = (v: number) => `${(v / 100000000).toFixed(1)}억`;

    const renderList = (list: any[], title: string, subtitle: string, isHigh: boolean) => (
        <div style={{ flex: 1, minWidth: '320px', backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
            <div style={{ marginBottom: '20px' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>{title}</h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>{subtitle}</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {list.length === 0 && <div style={{ color: '#94a3b8', fontSize: '0.9rem', textAlign: 'center', padding: '40px 0' }}>조건에 맞는 단지가 없습니다.</div>}

                {list.map((item, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', backgroundColor: '#f8fafc', borderRadius: '8px', borderLeft: i < 3 ? `4px solid ${isHigh ? '#ef4444' : '#3b82f6'}` : '4px solid #cbd5e1' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ fontWeight: 800, width: '24px', color: i < 3 ? (isHigh ? '#ef4444' : '#3b82f6') : '#94a3b8' }}>{i + 1}</div>
                            <div>
                                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#1e293b' }}>{item.c_name} <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 'normal' }}>{item.type_name}</span></div>
                                <div style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
                                    실거래 <b>{formatPrice(item.recent_deal)}</b> <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>({item.deal_date})</span> <br />
                                    vs 현재호가 <b>{formatPrice(item.lowest_ask)}</b>
                                </div>
                            </div>
                        </div>
                        <div style={{ fontWeight: 800, color: isHigh ? '#ef4444' : '#3b82f6', backgroundColor: isHigh ? '#fee2e2' : '#dbeafe', padding: '6px 12px', borderRadius: '20px', fontSize: '0.95rem' }}>
                            {item.gap_pct > 0 ? '+' : ''}{item.gap_pct.toFixed(1)}%
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* 상단 주석 안내 문구 */}
            <div style={{ fontSize: '0.85rem', color: '#64748b', padding: '12px 16px', backgroundColor: '#f1f5f9', borderRadius: '8px', borderLeft: '3px solid #94a3b8' }}>
                💡 <b>시황 지표 산출 가이드:</b> 위 차트들과 랭킹은 500개 타입 전체의 단순 평균이 아닙니다. 쌍둥이 평형을 제외한 거래량 1위 <b>핵심 대표 평형 312곳</b>을 엄선하여, 그들의 순수 호가와 실거래가의 1:1 '중간값(Median)'을 추출함으로써 이상치(거품)를 완벽히 차단한 정밀 지표입니다.
            </div>

            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                {renderList(highList, "🔥 호가 vs 실거래 갭 (버티기 장세) TOP 10", "최근 6개월 체결가보다 현재 호가가 비싼 단지", true)}
                {renderList(lowList, "🧊 실거래 붕괴 (초급매 장세) TOP 10", "최근 6개월 체결가보다 현재 호가가 심하게 싼 단지", false)}
            </div>
        </div>
    );
}
