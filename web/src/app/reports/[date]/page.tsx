import React from 'react';
import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ReportComments from './ReportComments';

export const dynamic = 'force-dynamic';

export default async function ReportDetail({ params }: { params: { date: string } }) {
    const date = params.date;
    const reportPath = path.join(process.cwd(), 'src', 'data', 'reports', `report_${date}.md`);

    let content = "";
    let error = false;

    try {
        content = fs.readFileSync(reportPath, 'utf8');
    } catch (e) {
        error = true;
    }

    if (error) {
        return <div style={{ padding: '40px', color: 'var(--text-dark)', textAlign: 'center' }}>리포트를 찾을 수 없습니다.</div>;
    }

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px', fontFamily: 'var(--font-pretendard, sans-serif)' }}>
            <div style={{ marginBottom: '30px' }}>
                <Link href="/reports" style={{ color: 'var(--text-muted)', textDecoration: 'none', fontSize: '14px' }}>← 목록으로 돌아가기</Link>
            </div>

            <div style={{
                backgroundColor: 'var(--card-bg)',
                border: '1px solid var(--border-light)',
                borderRadius: '12px',
                padding: '40px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
                marginBottom: '40px'
            }}>
                <div style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '24px', marginBottom: '32px' }}>
                    <div style={{ color: 'var(--accent-color)', fontWeight: '600', fontSize: '14px', marginBottom: '8px' }}>RealFifty AI Reporter</div>
                    <h1 style={{ margin: 0, fontSize: '32px', fontWeight: '800', color: 'var(--text-dark)' }}>{date} 부동산 시황 요약 리포트</h1>
                </div>

                <div className="prose prose-invert max-w-none" style={{ lineHeight: '1.8' }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {content}
                    </ReactMarkdown>
                </div>
            </div>

            {/* Comments Section */}
            <ReportComments reportDate={date} />
        </div>
    );
}
