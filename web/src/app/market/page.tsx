import React from 'react';
import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import MacroIndexChart from '../MacroIndexChart';

export const dynamic = 'force-dynamic';

export default async function MarketOverview() {
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

    const macroPath = path.join(process.cwd(), 'src', 'data', 'macro_index.json');
    let macroData = [];
    try { macroData = JSON.parse(fs.readFileSync(macroPath, 'utf8')); } catch (e) { }

    return (
        <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px', fontFamily: 'var(--font-pretendard, sans-serif)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '30px' }}>
                <div>
                    <h1 style={{ fontSize: '32px', fontWeight: '800', margin: '0 0 8px 0', color: 'var(--text-dark)' }}>📊 종합 시황 및 거시 지표</h1>
                    <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '15px' }}>
                        서울 상위 50개 대장 아파트의 가격, 호가, 거래량 데이터를 종합한 리얼피프티 고유의 시장 분석 지표입니다.
                    </p>
                </div>
                <Link href="/" style={{ color: 'var(--text-muted)', textDecoration: 'none', fontSize: '14px', border: '1px solid var(--border-light)', padding: '8px 16px', borderRadius: '6px' }}>← 대시보드로 돌아가기</Link>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '30px', marginBottom: '60px' }}>
                <MacroIndexChart data={macroData} />
                {/* Placeholder for Volume Chart */}
                <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid var(--border-light)', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-dark)' }}>🌊 역대 최대치 대비 월간 거래량 추이 (준비중)</h2>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: 0 }}>과거 폭등장 최다 거래량 월과 현재를 비교한 시장 유동성 분석 (데이터 연동 예정)</p>
                    <div style={{ height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ccc', fontStyle: 'italic' }}>
                        Volume Component Loading...
                    </div>
                </div>
            </div>

            <h2 style={{ fontSize: '24px', fontWeight: '800', margin: '0 0 20px 0', color: 'var(--text-dark)', borderBottom: '2px solid var(--text-dark)', paddingBottom: '12px' }}>📰 일일 마켓 브리핑 리포트</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {reports.length === 0 && <div style={{ color: 'var(--text-muted)' }}>아직 발행된 리포트가 없습니다.</div>}
                {reports.map(date => (
                    <Link key={date} href={`/market/${date}`} style={{ textDecoration: 'none' }}>
                        <div style={{
                            padding: '24px',
                            backgroundColor: 'white',
                            border: '1px solid var(--border-light)',
                            borderRadius: '12px',
                            transition: 'all 0.2s',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            cursor: 'pointer',
                            boxShadow: '0 4px 10px rgba(0,0,0,0.02)'
                        }}>
                            <div>
                                <div style={{ fontSize: '14px', color: '#131b2e', fontWeight: '800', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>Market Report</div>
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
