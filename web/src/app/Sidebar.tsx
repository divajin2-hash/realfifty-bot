import React from 'react';
import Link from 'next/link';
import SearchInput from './SearchInput';

export default function Sidebar({ activePath }: { activePath: string }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo" style={{ padding: '32px 24px 12px 24px' }}>
                <Link href="/" style={{ textDecoration: 'none' }}>
                    <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                        Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
                    </div>
                </Link>
            </div>
            <div className="sidebar-menu" style={{ marginTop: '10px' }}>
                <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <div className={`menu-item ${activePath === '/' ? 'active' : ''}`}>📈 실시간 시장 현황</div>
                </Link>
                <Link href="/market" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <div className={`menu-item ${activePath === '/market' ? 'active' : ''}`}>📊 종합 시황 현황</div>
                </Link>
                <Link href="/report" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <div className={`menu-item ${activePath === '/report' ? 'active' : ''}`}>📝 데일리 리포트</div>
                </Link>
                <Link href="/news" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <div className={`menu-item ${activePath === '/news' ? 'active' : ''}`}>🔍 부동산 팩트체크</div>
                </Link>
                <div className="menu-item" style={{ cursor: 'not-allowed', opacity: 0.5 }}>🚨 급매물 알림 (준비중)</div>
                <div className="menu-item" style={{ cursor: 'not-allowed', opacity: 0.5 }}>⭐ 관심 단지 등록 (준비중)</div>
            </div>
            <div style={{ marginTop: 'auto', padding: '24px' }}>
                <SearchInput />
            </div>
        </aside>
    );
}
