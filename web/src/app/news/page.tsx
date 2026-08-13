import React from 'react';
import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import Sidebar from '../Sidebar';

export const dynamic = 'force-dynamic';

export default async function NewsFactCheckPage(props: any) {
    const searchParams = typeof props.searchParams === 'object' ? await props.searchParams : {};
    const targetDate = searchParams?.date;

    const newsPath = path.join(process.cwd(), 'src', 'data', 'factcheck_history.json');
    let allNews: any[] = [];

    try {
        if (fs.existsSync(newsPath)) {
            allNews = JSON.parse(fs.readFileSync(newsPath, 'utf8'));
        } else {
            const singlePath = path.join(process.cwd(), 'src', 'data', 'factcheck_news.json');
            if (fs.existsSync(singlePath)) {
                allNews = JSON.parse(fs.readFileSync(singlePath, 'utf8'));
            }
        }
    } catch (e) {
        console.error("News read error", e);
    }

    // 그룹화 로직 (날짜별)
    const groupedNews: Record<string, any[]> = {};
    allNews.forEach(news => {
        let d = "Unknown";
        try {
            d = new Date(news.pub_date).toISOString().split('T')[0];
        } catch (e) { }
        if (!groupedNews[d]) groupedNews[d] = [];
        groupedNews[d].push(news);
    });

    // 날짜 역순 정렬
    const sortedDates = Object.keys(groupedNews).sort((a, b) => b.localeCompare(a));
    const activeDate = (targetDate && sortedDates.includes(targetDate)) ? targetDate : (sortedDates[0] || "");
    const activeNewsList = activeDate ? groupedNews[activeDate] : [];

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/news" />
            <div className="main-content">
                <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 60px', fontFamily: 'var(--font-pretendard, sans-serif)' }}>
                    <div style={{ marginBottom: '40px' }}>
                        <h1 style={{ fontSize: '32px', fontWeight: '800', margin: '0 0 8px 0', color: 'var(--text-dark)' }}>🔍 조간 뉴스 팩트체크</h1>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '15px' }}>
                            실시간 뉴스의 본문과 헤드라인이 과장되었는지, RealFifty의 팩트 데이터로 철저하게 검증합니다.
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: '40px' }}>
                        {/* Main Active Factchecks */}
                        <div style={{ flex: '1', minWidth: '0', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                            {activeNewsList.length === 0 ? (
                                <div style={{ padding: '40px', textAlign: 'center', backgroundColor: 'white', borderRadius: '16px', border: '1px solid var(--border-light)' }}>
                                    해당 날짜에 생성된 팩트체크 데이터가 없습니다.
                                </div>
                            ) : (
                                activeNewsList.map((news, idx) => (
                                    <div key={idx} style={{
                                        backgroundColor: 'white',
                                        border: '1px solid var(--border-light)',
                                        borderRadius: '16px',
                                        padding: '32px',
                                        boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
                                    }}>
                                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
                                            <span style={{
                                                backgroundColor: news.verdict_type.includes('과장') || news.verdict_type.includes('거짓') ? '#ffeaeb' : '#e8f5e9',
                                                color: news.verdict_type.includes('과장') || news.verdict_type.includes('거짓') ? '#ba1a1a' : '#006b54',
                                                padding: '6px 12px', borderRadius: '4px', fontSize: '13px', fontWeight: '800'
                                            }}>{news.verdict_type}</span>
                                            <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>{news.source} · {new Date(news.pub_date).toLocaleDateString()}</span>
                                            <a href={news.link} target="_blank" rel="noreferrer" style={{ marginLeft: 'auto', fontSize: '13px', color: '#005fb0', textDecoration: 'none', fontWeight: '700', padding: '6px 12px', border: '1px solid #005fb0', borderRadius: '4px', transition: 'all 0.2s' }}>
                                                원문 기사 읽기 🔗
                                            </a>
                                        </div>
                                        <h2 style={{ fontSize: '22px', fontWeight: '800', marginBottom: '16px', lineHeight: '1.4' }}>
                                            📰 기사 헤드라인: "{news.title}"
                                        </h2>
                                        <div style={{ padding: '16px', backgroundColor: '#fafafa', borderLeft: '4px solid #ddd', marginBottom: '24px', fontSize: '14px', color: '#555', lineHeight: '1.6' }}>
                                            <strong>💡 기사 본문 요약:</strong> {news.body_summary}
                                        </div>

                                        <div style={{ backgroundColor: '#f5f7fa', padding: '24px', borderRadius: '12px', position: 'relative' }}>
                                            <div style={{ position: 'absolute', top: '-14px', left: '24px', backgroundColor: '#005fb0', color: 'white', padding: '4px 12px', borderRadius: '4px', fontSize: '13px', fontWeight: '800' }}>
                                                REALFIFTY 팩트 검증 완료 ({activeDate})
                                            </div>
                                            <p style={{ fontSize: '15px', color: '#131b2e', lineHeight: '1.7', marginTop: '10px', marginBottom: 0, whiteSpace: 'pre-wrap' }}>
                                                {news.factcheck_content}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        {/* Sidebar List of FactCheck Dates */}
                        <div style={{ width: '280px', flexShrink: 0 }}>
                            <h3 style={{ fontSize: '18px', fontWeight: '800', marginBottom: '16px' }}>과거 팩트체크 아카이브</h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                {sortedDates.map(date => (
                                    <Link key={date} href={`/news?date=${date}`} style={{ textDecoration: 'none' }}>
                                        <div style={{
                                            padding: '16px',
                                            backgroundColor: date === activeDate ? '#f1f8ff' : 'white',
                                            border: date === activeDate ? '1px solid #005fb0' : '1px solid var(--border-light)',
                                            borderRadius: '8px',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s ease',
                                        }}>
                                            <div style={{
                                                fontSize: '12px',
                                                color: date === activeDate ? '#005fb0' : 'var(--text-muted)',
                                                fontWeight: date === activeDate ? '700' : 'normal'
                                            }}>{date}</div>
                                            <div style={{
                                                fontSize: '15px',
                                                fontWeight: '800',
                                                marginTop: '4px',
                                                color: date === activeDate ? '#005fb0' : 'var(--text-dark)'
                                            }}>
                                                {groupedNews[date].length}건의 기사 검증 {date === activeDate && '📖'}
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                                {sortedDates.length === 0 && <div style={{ fontSize: '14px', color: 'var(--text-muted)' }}>이전 기록이 없습니다.</div>}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
