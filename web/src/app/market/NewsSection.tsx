"use client";
import React from 'react';

export default function NewsSection({ newsData }: { newsData: any[] }) {
    if (!newsData || newsData.length === 0) return null;

    return (
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', boxShadow: '0 4px 20px rgba(0,0,0,0.03)', marginTop: '30px', marginBottom: '60px' }}>
            <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>📰 오늘의 부동산 핫 실시간 속보</h2>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>구글 뉴스 AI 엔진이 실시간으로 긁어온 부동산 이슈</p>
                </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {newsData.slice(0, 7).map((item, i) => (
                    <a key={i} href={item.link} target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', padding: '12px', borderBottom: i === 6 ? 'none' : '1px solid #f1f5f9', cursor: 'pointer', transition: 'background 0.2s' }} className="hover:bg-slate-50">
                            <div style={{ fontSize: '1rem', color: '#334155', lineHeight: '1.4', flex: 1 }}>
                                {item.title}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#94a3b8', whiteSpace: 'nowrap', marginLeft: '16px' }}>
                                {item.source}
                            </div>
                        </div>
                    </a>
                ))}
            </div>
        </div>
    );
}
