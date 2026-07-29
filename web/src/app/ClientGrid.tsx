"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

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

function ComplexCard({ complex, stats, rank }: { complex: any, stats: any[], rank: number }) {
    const router = useRouter();
    const [dealIdx, setDealIdx] = useState(0);

    if (stats.length === 0) return null;
    const activeStat = getRepresentativeStat(stats);

    const ath = activeStat.highest_deal_price;
    const absoluteRecent = activeStat.recent_deal_absolute;
    const currentAsk = activeStat.current_lowest_ask;
    const mddValue = activeStat.mdd_rate ? activeStat.mdd_rate.toFixed(1) : '0.0';

    const monthDeals = activeStat.month_deals || [];

    const formattedDeals = monthDeals.map((t: any) => ({
        price: t.price,
        date: formatDate(t.date),
        type: t.type,
        floor: t.floor || '-'
    }));

    useEffect(() => {
        setDealIdx(0);
        if (formattedDeals.length <= 1) return;
        const timer = setInterval(() => {
            setDealIdx((prev) => (prev + 1) % formattedDeals.length);
        }, 2800);
        return () => clearInterval(timer);
    }, [formattedDeals.length]);

    const currentDeal = formattedDeals[dealIdx];
    const dealAnimationKey = `deal-${dealIdx}`;

    const athDateStr = activeStat.highest_deal_date && activeStat.highest_deal_date.length >= 10 ? `${activeStat.highest_deal_date.substring(2, 4)}.${activeStat.highest_deal_date.substring(5, 7)}.${activeStat.highest_deal_date.substring(8, 10)}` : '-';
    const absDrop = (absoluteRecent && ath > 0 && absoluteRecent.price) ? (((ath - absoluteRecent.price) / ath) * 100).toFixed(1) : '0.0';

    const currentMonth = new Date().getMonth() + 1;

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
        <div className="ap-card" onClick={() => router.push(`/detail/${complex.id}`)}>
            <div className="card-header-navy">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: 0 }}>
                    <div className="live-indicator" style={{ flexShrink: 0 }}></div>
                    <div style={{
                        fontSize: complex.name.length > 10 ? '0.95rem' : (complex.name.length > 8 ? '1.05rem' : 'inherit'),
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        letterSpacing: complex.name.length > 8 ? '-1px' : 'inherit'
                    }}>
                        {complex.name}
                    </div>
                </div>
                <div style={{ background: '#ffb4ab', color: '#ba1a1a', padding: '4px 8px', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 900 }}>
                    {rank}위
                </div>
            </div>

            <div className="card-body">
                <div className="rep-badge">
                    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"></path></svg>
                    대표 주력 타입 ({activeStat.match_key_area}㎡{activeStat.pyeong_name ? ` / ${activeStat.pyeong_name}㎡` : ''})
                </div>

                <div className="data-split">
                    <div className="data-block">
                        <span className="data-label">역대최고가 <span className="num-font" style={{ fontSize: "0.85em", opacity: 0.6 }}>({athDateStr})</span></span>
                        <span className="data-value">
                            <span className="num-font">{formatPriceNum(ath)}</span><span className="kr-unit">억</span>
                        </span>
                        <span className="data-value-sub" style={{ fontSize: "0.85rem" }}>최근 실거래 <span className="num-font" style={{ fontSize: "0.9em", opacity: 0.75 }}>({lastDealDateStr})</span>: <span className="num-font">{absoluteRecent ? formatPriceNum(absoluteRecent.price) : '-'}</span><span className="kr-unit">억</span></span>
                    </div>
                    <div className="alert-box">
                        {absDrop === '0.0' && absoluteRecent && absoluteRecent.price ? (
                            <div style={{ paddingTop: '5px', fontSize: '1.2rem', fontWeight: 800, color: '#ba1a1a', whiteSpace: 'nowrap', textAlign: 'center' }}>최고가</div>
                        ) : (
                            <>
                                <div style={{ fontSize: '0.65rem', color: '#ba1a1a', whiteSpace: 'nowrap' }}>고점대비 실거래</div>
                                <div className="num-font" style={{ marginTop: '4px', fontSize: '1.4rem' }}>{absDrop === '0.0' ? '-' : `-${absDrop}%`}</div>
                            </>
                        )}
                    </div>
                </div>

                <div className="dashed-divider"></div>

                <div className="data-block" style={{ minHeight: '70px' }}>
                    <span className="data-label">당월({currentMonth}월) 체결된 실거래</span>

                    {formattedDeals.length > 0 ? (
                        <div key={dealAnimationKey} style={{ animation: 'flashUpdate 0.8s ease-out', padding: '6px 8px', marginLeft: '-8px', borderRadius: '4px', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                            <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#191c1e' }}>
                                <span className="num-font">{formatPriceNum(currentDeal.price)}</span><span className="kr-unit">억</span>
                            </span>
                            <span style={{ fontSize: '0.85rem', color: '#76777d' }}>({currentDeal.floor}층 {currentDeal.date} / {currentDeal.type === '중개거래' ? '중개' : '직거래'})</span>
                        </div>
                    ) : (
                        <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#76777d' }}>
                            이전 거래일(<span className="num-font">{lastDealDateStr}</span>) 이후로
                            <div className="freeze-warning" style={{ fontSize: '1.1rem', marginTop: '4px' }}>
                                <span className="num-font">{diffDays}</span>일간 거래 없음
                            </div>
                        </div>
                    )}
                </div>

                <div className="data-split" style={{ marginTop: '15px' }}>
                    <div className="data-block">
                        <span className="data-label">현재 시장 최저 호가</span>
                        <span className="data-value" style={{ fontSize: '1.3rem' }}>
                            <span className="num-font">{formatPriceNum(currentAsk)}</span><span className="kr-unit">억</span>
                        </span>
                    </div>
                    <div className="alert-box safe" style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {mddValue === '0.0' && currentAsk > 0 ? (
                            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#131b2e', whiteSpace: 'nowrap' }}>최고가</div>
                        ) : (
                            <div>
                                <div style={{ fontSize: '0.6rem', color: '#131b2e', opacity: 0.8, whiteSpace: 'nowrap', textAlign: 'right' }}>고점대비 호가</div>
                                <div className="num-font" style={{ marginTop: '2px', fontSize: '1.2rem' }}>{mddValue === '0.0' ? '-' : `${mddValue}%`}</div>
                            </div>
                        )}
                    </div>
                </div>

            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
        @keyframes flashUpdate {
          0% { background-color: #ffdad6; color: #ba1a1a; transform: translateX(-4px); }
          50% { background-color: transparent; color: #191c1e; transform: translateX(0); }
          100% { background-color: transparent; color: inherit; }
        }
        @keyframes blinkIndicator {
          0% { opacity: 0.3; }
          50% { opacity: 1; box-shadow: 0 0 8px #ffdad6; }
          100% { opacity: 0.3; }
        }
        .live-indicator {
          width: 8px; height: 8px; 
          border-radius: 50%; 
          background-color: #ffb4ab;
          animation: blinkIndicator 1.5s infinite;
        }
      `}} />
        </div>
    );
}

export default function ClientGrid({ groupedData }: { groupedData: any[] }) {
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        const handler = (e: any) => setSearchQuery(e.detail);
        window.addEventListener('kb50_search', handler);
        return () => window.removeEventListener('kb50_search', handler);
    }, []);

    const filtered = groupedData.filter(g => g.complex.name.replace(/\s+/g, '').includes(searchQuery.replace(/\s+/g, '')));

    return (
        <div>

            <div className="grid-layout">
                {filtered.map((group) => (
                    <ComplexCard key={group.complex.id} complex={group.complex} stats={group.stats} rank={group.rank} />
                ))}
                {filtered.length === 0 && (
                    <div style={{ gridColumn: '1 / -1', padding: '60px', textAlign: 'center', color: '#76777d', fontSize: '1.2rem', fontWeight: 700 }}>
                        검색 결과가 없습니다.
                    </div>
                )}
            </div>
        </div>
    );
}