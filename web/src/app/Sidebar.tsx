'use client';
import React from 'react';
import {useMember} from './MemberProvider';
import BrandLogo from './BrandLogo';
import FeedbackButton from './FeedbackButton';
import Link from 'next/link';
import { Activity, LayoutDashboard, Building2, FileText, CheckSquare, BookOpen } from 'lucide-react';

export default function Sidebar({ activePath }: { activePath: string }) {
    const {user,ready}=useMember();
    const accountLabel=!ready?'계정 확인 중…':user?'내 정보':'로그인';

    return (
        <>
            {/* 1. Desktop Sidebar */}
            <aside className="sidebar desktop-only">
                <div className="sidebar-logo-area">
                    <BrandLogo />

                </div>

                <nav className="sidebar-menu">
                    <Link href="/" className={`nav-item ${activePath === '/' ? 'active' : ''}`}>
                        <Activity size={18} /> 오늘의 시장
                    </Link>
                    <Link href="/market" className={`nav-item ${activePath === '/market' ? 'active' : ''}`}>
                        <LayoutDashboard size={18} /> 시장 분석
                    </Link>
                    <Link href="/complex" className={`nav-item ${activePath === '/complex' ? 'active' : ''}`}>
                        <Building2 size={18} /> 단지 탐색
                    </Link>
                    <Link href="/report" className={`nav-item ${activePath === '/report' ? 'active' : ''}`}>
                        <FileText size={18} /> 리포트
                    </Link>
                    <Link href="/news" className={`nav-item ${activePath === '/news' ? 'active' : ''}`}>
                        <CheckSquare size={18} /> 팩트체크
                    </Link>
                    <Link href="/guide" aria-current={activePath === "/guide" ? "page" : undefined} className={`nav-item ${activePath === "/guide" ? "active" : ""}`}><BookOpen size={18}/> 이용 가이드</Link>
                </nav>

                <Link href="/account" className="member-account-link">{accountLabel} →</Link>
                <div className="sidebar-feedback"><FeedbackButton/><Link href="/improvements">개선 소식 →</Link></div>
                <div className="sidebar-footer">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span>DATA SOURCE</span>
                        <span style={{ color: 'var(--color-cyan)', fontWeight: 700 }}>실거래 · 매물 호가</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>ANALYSIS SCOPE</span>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 700 }}>대표 50개 단지</span>
                    </div>
                </div>
            </aside>

            {/* 2. Mobile Top Header */}
            <div className="mobile-top-header mobile-only">
                <BrandLogo />
                <Link href="/account" className="mobile-account-link">{accountLabel}</Link>
            </div>

            {/* 3. Mobile Bottom Nav */}
            <nav className="mobile-bottom-nav mobile-only">
                <Link href="/" className={`mobile-nav-item ${activePath === '/' ? 'active' : ''}`}>
                    <Activity size={20} />
                    오늘의 시장
                </Link>
                <Link href="/market" className={`mobile-nav-item ${activePath === '/market' ? 'active' : ''}`}>
                    <LayoutDashboard size={20} />
                    시장 분석
                </Link>
                <Link href="/complex" className={`mobile-nav-item ${activePath === '/complex' ? 'active' : ''}`}>
                    <Building2 size={20} />
                    단지 탐색
                </Link>
                <Link href="/report" className={`mobile-nav-item ${activePath === '/report' ? 'active' : ''}`}>
                    <FileText size={20} />
                    리포트
                </Link>
                <Link href="/news" className={`mobile-nav-item ${activePath === '/news' ? 'active' : ''}`}>
                    <CheckSquare size={20} />
                    팩트체크
                </Link>
            </nav>
        </>
    );
}
