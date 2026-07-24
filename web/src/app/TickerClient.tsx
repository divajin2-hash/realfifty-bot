"use client";
import React, { useState, useEffect } from 'react';

export default function TickerClient({ items }: { items: { name: string, drop: string, isSevere: boolean, rank: number }[] }) {
    const ITEMS_PER_PAGE = 4;
    const pages = [];
    for (let i = 0; i < items.length; i += ITEMS_PER_PAGE) {
        pages.push(items.slice(i, i + ITEMS_PER_PAGE));
    }

    const [pageIdx, setPageIdx] = useState(0);
    const [isFading, setIsFading] = useState(false);

    useEffect(() => {
        if (pages.length <= 1) return; // No need to slide if only 1 page
        const timer = setInterval(() => {
            setIsFading(true);
            setTimeout(() => {
                setPageIdx((prev) => (prev + 1) % pages.length);
                setIsFading(false);
            }, 600);
        }, 5000);
        return () => clearInterval(timer);
    }, [pages.length]);

    const currentPage = pages[pageIdx];
    if (!currentPage) return null;

    return (
        <div className="top-ticker" style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: '0 24px', overflow: 'hidden' }}>
            <span style={{ fontWeight: 800, color: '#ffdad6', marginRight: '30px', flexShrink: 0 }}>🔥 평균 하회 위험 단지</span>
            <div style={{ flex: 1, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', transition: 'opacity 0.6s ease-in-out', opacity: isFading ? 0 : 1 }}>
                {currentPage.map((item, idx) => (
                    <span key={idx} style={{ fontSize: '0.95rem', display: 'flex', alignItems: 'center', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                        <span className="num-font" style={{ display: 'inline-block', width: '22px', height: '22px', background: 'rgba(255,218,214,0.15)', color: '#ffdad6', borderRadius: '4px', textAlign: 'center', lineHeight: '22px', fontSize: '0.75rem', fontWeight: 800, marginRight: '8px' }}>
                            {item.rank}
                        </span>
                        <strong style={{ fontWeight: 800, overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '140px' }}>{item.name}</strong>
                        <span className="num-font" style={{ color: item.isSevere ? '#ffb4ab' : '#ffffff', marginLeft: '6px', fontWeight: 800, textShadow: item.isSevere ? '0 0 10px rgba(255,180,171,0.5)' : 'none' }}>
                            {item.drop}%
                        </span>
                    </span>
                ))}
            </div>
        </div>
    );
}
