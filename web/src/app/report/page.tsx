import React from 'react';
import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Sidebar from '../Sidebar';

export const dynamic = 'force-dynamic';

export default async function ReportPage(props: any) {
    const searchParams = typeof props.searchParams === 'object' ? await props.searchParams : {};
    const targetDate = searchParams?.date;

    const reportsDir = path.join(process.cwd(), 'src', 'data', 'reports');
    let reports: string[] = [];
    let activeReportContent = "";
    let activeDate = "";

    try {
        if (fs.existsSync(reportsDir)) {
            reports = fs.readdirSync(reportsDir)
                .filter(file => file.endsWith('.md'))
                .map(file => file.replace('report_', '').replace('.md', ''))
                .sort((a, b) => b.localeCompare(a)); // 최신순 정렬

            if (reports.length > 0) {
                // 사용자가 요청한 날짜가 있으면 그걸로, 없으면 최신날짜(reports[0])로
                activeDate = (targetDate && reports.includes(targetDate)) ? targetDate : reports[0];
                const reportPath = path.join(reportsDir, `report_${activeDate}.md`);
                if (fs.existsSync(reportPath)) {
                    activeReportContent = fs.readFileSync(reportPath, 'utf8');
                }
            }
        }
    } catch (e) {
        console.error(e);
    }

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/report" />
            <div className="main-content">
                <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 60px', fontFamily: 'var(--font-pretendard, sans-serif)' }}>
                    <div style={{ marginBottom: '40px' }}>
                        <h1 style={{ fontSize: '32px', fontWeight: '800', margin: '0 0 8px 0', color: 'var(--text-dark)' }}>📝 데일리 마켓 리포트</h1>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '15px' }}>
                            리얼피프티 분석가가 매일 아침 작성하는 시황 요약 리포트입니다.
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: '40px' }}>
                        {/* Main Active Report */}
                        <div style={{ flex: '1', minWidth: '0' }}>
                            {activeReportContent ? (
                                <div style={{
                                    backgroundColor: 'white',
                                    border: '1px solid var(--border-light)',
                                    borderRadius: '16px',
                                    padding: '40px',
                                    boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
                                }}>
                                    <div style={{ borderBottom: '2px solid var(--text-dark)', paddingBottom: '24px', marginBottom: '32px' }}>
                                        <div style={{ color: '#005fb0', fontWeight: '800', fontSize: '14px', marginBottom: '8px', letterSpacing: '1px' }}>REALFIFTY DAILY REPORT</div>
                                        <h2 style={{ margin: 0, fontSize: '28px', fontWeight: '800', color: 'var(--text-dark)' }}>{activeDate} 부동산 시황 요약</h2>
                                    </div>
                                    <div className="prose prose-invert max-w-none report-content" style={{ lineHeight: '1.8', color: '#131b2e' }}>
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {activeReportContent}
                                        </ReactMarkdown>
                                    </div>
                                </div>
                            ) : (
                                <div style={{ padding: '40px', textAlign: 'center', backgroundColor: 'white', borderRadius: '16px', border: '1px solid var(--border-light)' }}>
                                    생성된 리포트가 없습니다.
                                </div>
                            )}
                        </div>

                        {/* Sidebar List of Reports */}
                        <div style={{ width: '280px', flexShrink: 0 }}>
                            <h3 style={{ fontSize: '18px', fontWeight: '800', marginBottom: '16px' }}>지난 리포트 탐색</h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                {reports.map(date => (
                                    <Link key={date} href={`/report?date=${date}`} style={{ textDecoration: 'none' }}>
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
                                                {date} 마켓 브리핑 {date === activeDate && '읽는 중 📖'}
                                            </div>
                                        </div>
                                    </Link>
                                ))}
                                {reports.length === 0 && <div style={{ fontSize: '14px', color: 'var(--text-muted)' }}>이전 리포트가 없습니다.</div>}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
