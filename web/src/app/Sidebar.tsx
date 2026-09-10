import React from 'react';
import Link from 'next/link';
import { Activity, LayoutDashboard, Building2, FileText, CheckSquare } from 'lucide-react';

export default function Sidebar({ activePath }: { activePath: string }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo-area">
                <Link href="/" style={{ textDecoration: 'none' }}>
                    <div className="sidebar-logo">
                        TERMINAL MATRIX<br />
                        <span style={{ color: 'var(--text-dark)' }}>SEOUL 50 RADAR</span>
                    </div>
                </Link>
                <div className="sidebar-index">
                    CORE INDEX<br />
                    <span className="sidebar-index-value">1,248.60 bps</span>
                </div>
            </div>

            <nav className="sidebar-menu">
                <Link href="/" className={`nav-item ${activePath === '/' ? 'active' : ''}`}>
                    <Activity size={18} /> TODAY
                </Link>
                <Link href="/market" className={`nav-item ${activePath === '/market' ? 'active' : ''}`}>
                    <LayoutDashboard size={18} /> MARKET
                </Link>
                <Link href="/complex" className={`nav-item ${activePath === '/complex' ? 'active' : ''}`}>
                    <Building2 size={18} /> COMPLEX
                </Link>
                <Link href="/report" className={`nav-item ${activePath === '/report' ? 'active' : ''}`}>
                    <FileText size={18} /> REPORT
                </Link>
                <Link href="/news" className={`nav-item ${activePath === '/news' ? 'active' : ''}`}>
                    <CheckSquare size={18} /> FACT CHECK
                </Link>
            </nav>

            <div className="sidebar-footer">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>FEED LATENCY</span>
                    <span style={{ color: 'var(--color-cyan)', fontWeight: 700 }}>12ms</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>REGIME ENGINE</span>
                    <span style={{ color: 'var(--color-down)', fontWeight: 700 }}>VOLATILITY-A</span>
                </div>
            </div>
        </aside>
    );
}
