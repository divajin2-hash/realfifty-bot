import React from 'react';
import fs from 'fs';
import path from 'path';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default async function ReportsIndex() {
    const reportsDir = path.join(process.cwd(), 'src', 'data', 'reports');
    let reports: string[] = [];

    try {
        if (fs.existsSync(reportsDir)) {
            reports = fs.readdirSync(reportsDir)
                .filter(file => file.endsWith('.md'))
                .map(file => file.replace('report_', '').replace('.md', ''))
                .sort((a, b) => b.localeCompare(a));
        }
    } catch (e) { }

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px', fontFamily: 'var(--font-pretendard, sans-serif)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                <h1 style={{ fontSize: '28px', fontWeight: '800', margin: 0, color: 'var(--text-dark)' }}>📰 일일 시황 리포트</h1>
                <Link href="/" style={{ color: 'var(--text-muted)', textDecoration: 'none', fontSize: '14px', border: '1px solid var(--border-light)', padding: '6px 12px', borderRadius: '6px' }}>← 대시보드로 돌아가기</Link>
            </div>
            <p style={{ color: 'var(--text-muted)', marginBottom: '40px' }}>
                매일 밤 자정, AI 에이전트가 서울 상위 50개 대장 아파트의 데이터를 심층 분석하여 전달하는 마켓 브리핑입니다.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {reports.length === 0 && <div style={{ color: 'var(--text-muted)' }}>아직 발행된 리포트가 없습니다.</div>}
                {reports.map(date => (
                    <Link key={date} href={`/reports/${date}`} style={{ textDecoration: 'none' }}>
                        <div style={{
                            padding: '24px',
                            backgroundColor: 'var(--card-bg)',
                            border: '1px solid var(--border-light)',
                            borderRadius: '12px',
                            transition: 'all 0.2s',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            cursor: 'pointer',
                            boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
                        }} className="hover:border-blue-500 hover:bg-gray-900">
                            <div>
                                <div style={{ fontSize: '14px', color: 'var(--accent-color)', fontWeight: '600', marginBottom: '8px' }}>Market Briefing</div>
                                <div style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-dark)' }}>{date} 부동산 시황 요약 리포트</div>
                            </div>
                            <div style={{ color: 'var(--text-muted)' }}>→</div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
}
