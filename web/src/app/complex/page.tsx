import React from 'react'
import '../globals.css'
import Sidebar from '../Sidebar'
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic';

export default async function ComplexDashboard() {
    const jsonPath = path.join(process.cwd(), 'src', 'data', 'kb50_stats.json');
    let rawData = [];
    try { rawData = JSON.parse(fs.readFileSync(jsonPath, 'utf8')); } catch (e) { }

    // Using Asia Athletes Village as the mock for the Complex detail page!
    const complexObj = (rawData as any[]).find(g => g.complex.name === '아시아선수촌') || rawData[0];
    const rep = complexObj.stats.find((s: any) => true); // just get the first one, or specific 124㎡

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/complex" />

            <div className="main-content" style={{ padding: '60px 50px', backgroundColor: 'var(--bg-main)', minHeight: '100vh', fontFamily: "'Pretendard Variable', sans-serif" }}>

                {/* 1. Header Area */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid var(--border-light)', paddingBottom: '12px' }}>
                    <div className="num-font" style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px' }}>
                        <div>METRO-SEOUL / SONGPA-GU / <span style={{ color: 'var(--color-cyan)', fontWeight: 800 }}>JAMSHIL-DONG / ASSET_ID: 11710-0086</span></div>
                    </div>
                    <div className="num-font" style={{ display: 'flex', gap: '12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <span style={{ color: 'var(--color-down)', fontWeight: 800 }}>● REGIME ALERT: DIVERGENCE MAX</span>
                        <span>| KB BLUECHIP 50 INDEX #14 | TERMINAL DEPTH: L3 LIVE</span>
                    </div>
                </div>

                {/* 2. Title & Main Status */}
                <div style={{ marginBottom: '40px' }}>
                    <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                        <div className="num-font" style={{ background: 'rgba(0,240,255,0.1)', border: '1px solid var(--color-cyan)', color: 'var(--color-cyan)', padding: '2px 8px', fontSize: '0.7rem' }}>SEOUL BLUECHIP TIER-1</div>
                        <div className="num-font" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-light)', color: 'var(--text-muted)', padding: '2px 8px', fontSize: '0.7rem' }}>재건축 대장단지 동조</div>
                        <div className="num-font" style={{ background: 'var(--color-down)', color: 'var(--bg-card)', padding: '2px 8px', fontSize: '0.7rem', fontWeight: 800 }}>HIGH SPREAD SPREAD +21.4%</div>
                    </div>
                    <h1 style={{ fontSize: '3rem', fontWeight: 900, lineHeight: 1.1, color: 'var(--text-dark)', letterSpacing: '-2px', marginBottom: '8px' }}>
                        아시아선수촌아파트 <span style={{ color: 'var(--color-cyan)', fontWeight: 400 }}>Asia Athletes Village</span>
                    </h1>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', gap: '16px', alignItems: 'center' }}>
                        <span className="num-font" style={{ color: 'var(--text-primary)', fontWeight: 800 }}>124A㎡ <span style={{ fontWeight: 400, color: 'var(--text-muted)' }}>(공급 46평 / 전용 134.48㎡)</span></span>
                        <span>⊙ 서울특별시 송파구 올림픽로 86 (잠실동)</span>
                        <span>• 준공 1986년 (18개동 / 1,356세대)</span>
                        <span>• 용적률 152% (대지지분 극상)</span>
                    </div>

                    {/* Top Stats Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr) 1.5fr', gap: '1px', backgroundColor: 'var(--border-light)', border: '1px solid var(--border-light)', marginTop: '32px' }}>
                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>RECENT ACTUAL TRADE<br />(최근 실거래가)</span>
                                <span>2026.07.09</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--color-cyan)', letterSpacing: '-1px', marginBottom: '16px' }}>
                                34.5<span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 400 }}>억원</span> <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.05)', padding: '4px 8px', borderRadius: '4px', color: 'var(--text-primary)' }}>4층 체결</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                                <span>평당 환산단가</span>
                                <span style={{ color: 'var(--text-primary)' }}>7,598 만원/평</span>
                            </div>
                        </div>

                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>CURRENT MIN ASKING<br />(현재 최저호가)</span>
                                <span style={{ color: 'var(--color-cyan)', fontWeight: 800 }}>LIVE<br />ORDERBOOK</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-dark)', letterSpacing: '-1px', marginBottom: '16px' }}>
                                41.9<span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 400 }}>억원</span> <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.05)', padding: '4px 8px', borderRadius: '4px', color: 'var(--text-primary)' }}>8층 매물</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                                <span>고점 대비 매도호가 하락률</span>
                                <span style={{ color: 'var(--text-primary)' }}>-5.8% (방어)</span>
                            </div>
                        </div>

                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>PEAK RETRACEMENT<br />(고점 대비 하락폭)</span>
                                <span style={{ color: 'var(--color-down)' }}>최고가<br />44.5억</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-dark)', letterSpacing: '-1px', marginBottom: '16px' }}>
                                -22.4<span style={{ fontSize: '1rem', fontWeight: 400 }}>%</span> <span style={{ fontSize: '0.8rem', background: 'rgba(255,123,114,0.1)', color: 'var(--color-down)', padding: '4px 8px', borderRadius: '4px' }}>-10.0억원</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                                <span>송파구 역대 하락폭 1위</span>
                                <span style={{ color: 'var(--text-primary)' }}>-11.2% 대비 급락</span>
                            </div>
                        </div>

                        <div style={{ padding: '24px', background: 'var(--bg-card)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>SPREAD DIVERGENCE<br />(실거래↔호가 괴리)</span>
                                <span style={{ color: 'var(--color-down)' }}>SEOUL<br />#1 GAP</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-dark)', letterSpacing: '-1px', marginBottom: '16px' }}>
                                +21.4<span style={{ fontSize: '1rem', fontWeight: 400 }}>%</span> <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)', padding: '4px 8px', borderRadius: '4px' }}>+7.4억원 차이</span>
                            </div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                                <span>시장 생태계 붕괴</span>
                                <span style={{ color: 'var(--text-primary)' }}>호가 왜곡 및 매수 관망</span>
                            </div>
                        </div>

                        <div style={{ padding: '24px', background: 'var(--bg-main)' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px' }}>QUANTITATIVE VERDICT SCORE: 28/100</div>
                            <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '16px' }}>
                                <div style={{ fontSize: '2rem' }}>⚠️</div>
                                <div>
                                    <div className="num-font" style={{ fontSize: '1.2rem', color: 'var(--color-warning)', fontWeight: 800, letterSpacing: '2px' }}>CAUTION</div>
                                    <div className="num-font" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>LIQUIDITY FREEZE</div>
                                </div>
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                                호가-체결가 괴리 극대화 구간 진입 (매수 관망 추천)
                            </div>
                        </div>
                    </div>
                </div>

                {/* 3. Valuation Chart & Freeze Metric */}
                <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '32px', marginBottom: '40px' }}>
                    {/* Valuation Line Chart */}
                    <div style={{ background: 'var(--bg-card)', padding: '32px', border: '1px solid var(--border-light)' }}>
                        <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                            <div>
                                <div style={{ color: 'var(--color-cyan)', fontSize: '0.75rem', letterSpacing: '1px', marginBottom: '4px' }}>VALUATION SPREAD VISUALIZER · 2024.01 - 2026.09 (3Y HORIZON)</div>
                                <div style={{ fontSize: '1.2rem', color: 'var(--text-dark)', fontWeight: 800 }}>실거래가 vs 최저호가 가격 괴리 (Divergence) 분석</div>
                            </div>
                            <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><div style={{ width: '12px', height: '2px', background: 'var(--color-cyan)' }}></div> 실거래 체결가</div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><div style={{ width: '12px', height: '2px', background: 'rgba(255,255,255,0.4)', borderTop: '2px dashed var(--text-dark)' }}></div> 최저 등록 호가</div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><div style={{ width: '12px', height: '12px', background: 'var(--color-down)' }}></div> 스프레드 갭 (+7.4억)</div>
                            </div>
                        </div>

                        <div style={{ height: '300px', border: '1px solid var(--border-light)', position: 'relative', background: 'var(--bg-main)' }}>
                            <svg width="100%" height="100%" viewBox="0 0 800 300" preserveAspectRatio="none">
                                {/* Asking Line (Dashed) */}
                                <path d="M 0 180 Q 200 100 400 50 L 600 120 L 800 120" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="3" strokeDasharray="6,6" />
                                {/* Real Deal Line */}
                                <path d="M 0 170 Q 200 90 400 50 L 600 250 L 800 250" fill="none" stroke="var(--color-cyan)" strokeWidth="4" />

                                {/* Gap Indicator Block */}
                                <rect x="680" y="140" width="100" height="40" fill="var(--color-down)" opacity="0.2" stroke="var(--color-down)" strokeDasharray="4" />
                                <text x="730" y="165" fill="var(--color-down)" fontSize="14" fontWeight="800" textAnchor="middle" className="num-font">갭: +7.4억 (+21.4%)</text>
                                <line x1="730" y1="120" x2="730" y2="250" stroke="var(--color-down)" strokeWidth="2" strokeDasharray="4" />

                                {/* Points */}
                                <circle cx="400" cy="50" r="6" fill="#fff" stroke="var(--color-cyan)" strokeWidth="2" />
                                <circle cx="800" cy="120" r="6" fill="#fff" stroke="rgba(255,255,255,0.4)" strokeWidth="2" />
                                <circle cx="600" cy="250" r="6" fill="var(--color-cyan)" />
                            </svg>
                            <div className="num-font" style={{ position: 'absolute', top: '20px', left: '48%', color: 'var(--text-muted)', fontSize: '0.75rem' }}>PEAK 44.5억</div>
                            <div className="num-font" style={{ position: 'absolute', top: '100px', right: '10%', color: 'var(--text-primary)', fontSize: '0.8rem' }}>버티기 호가 41.9억</div>
                            <div className="num-font" style={{ position: 'absolute', bottom: '60px', right: '30%', color: 'var(--color-cyan)', fontSize: '0.8rem' }}>최근 실거래 34.5억 (급매)</div>

                            <div className="num-font" style={{ position: 'absolute', bottom: '10px', width: '100%', display: 'flex', justifyContent: 'space-around', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                <span>2024.01</span><span>2024.07</span><span>2025.01</span><span>2025.07 (전고점)</span><span>2026.01</span><span style={{ color: 'var(--color-down)' }}>2026.07 (급락거래)</span><span style={{ color: 'var(--color-cyan)' }}>2026.09 (현재 호가)</span>
                            </div>
                        </div>

                        <div className="num-font" style={{ marginTop: '24px', display: 'flex', gap: '16px', background: 'rgba(255,255,255,0.03)', padding: '16px', border: '1px solid var(--border-light)' }}>
                            <div style={{ color: 'var(--text-muted)' }}>ⓘ</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', lineHeight: 1.6, flex: 1 }}>
                                매수측은 34.5억을 기준 삼고, 매도측은 41.9억을 마지노선으로 고수하며 체결 호가 스프레드가 극도로 확대되어 있습니다.
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                INDEX<br />COEFFICIENT:<br />0.023
                            </div>
                        </div>
                    </div>

                    {/* Liquidity Freeze Metric */}
                    <div style={{ background: 'var(--bg-card)', padding: '32px', border: '1px solid var(--border-light)' }}>
                        <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8렘', color: 'var(--color-down)', fontWeight: 800, marginBottom: '8px' }}>
                            <span>LIQUIDITY FREEZE METRIC</span><span>CRITICAL GAUGE</span>
                        </div>
                        <div style={{ fontSize: '1.2rem', color: 'var(--text-dark)', fontWeight: 800, marginBottom: '8px' }}>거래 공백 모니터링</div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '32px' }}>직전 거래 체결 후 신규 실거래 등록 부재 기간</div>

                        {/* Custom Slider */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px', padding: '0 8px' }} className="num-font">
                            <span>2026.07.09 최근 거래</span><span>2026.09.10 오늘 (현재)</span>
                        </div>
                        <div style={{ height: '8px', background: 'var(--border-light)', borderRadius: '4px', position: 'relative', marginBottom: '24px' }}>
                            <div style={{ position: 'absolute', top: 0, left: 0, height: '100%', width: '100%', background: 'linear-gradient(90deg, var(--color-cyan) 0%, var(--color-down) 100%)', borderRadius: '4px' }}></div>
                            <div style={{ position: 'absolute', right: '-4px', top: '-4px', width: '16px', height: '16px', backgroundColor: '#fff', borderRadius: '50%', border: '4px solid var(--color-down)', boxShadow: '0 0 10px var(--color-down)' }}></div>
                        </div>

                        <div className="num-font" style={{ textAlign: 'center', marginBottom: '40px' }}>
                            <div style={{ fontSize: '3rem', fontWeight: 900, color: 'var(--color-down)', lineHeight: 1 }}>63 <span style={{ fontSize: '1.2rem', color: 'var(--text-primary)' }}>DAYS <span style={{ color: 'var(--color-down)' }}>NO TRADE</span></span></div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', padding: '4px 16px', borderRadius: '4px', display: 'inline-block', marginTop: '12px' }}>평균 거래주기 14일 대비 4.5배 지연 중</div>
                        </div>

                        <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '16px' }}>RECENT 6-MONTH VOLUME (월별 총 TOTAL: 10건)</div>
                        {/* Fake Mini Bar Chart */}
                        <div style={{ display: 'flex', alignItems: 'flex-end', height: '60px', gap: '8px', borderBottom: '1px solid var(--border-light)' }}>
                            <div style={{ flex: 1, textAlign: 'center' }}><div style={{ height: '40px', background: 'var(--color-cyan)' }}></div><div style={{ fontSize: '0.65rem', marginTop: '4px' }}>4</div><div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>4월</div></div>
                            <div style={{ flex: 1, textAlign: 'center' }}><div style={{ height: '30px', background: 'var(--color-cyan)' }}></div><div style={{ fontSize: '0.65rem', marginTop: '4px' }}>3</div><div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>5월</div></div>
                            <div style={{ flex: 1, textAlign: 'center' }}><div style={{ height: '20px', background: 'var(--color-cyan)' }}></div><div style={{ fontSize: '0.65rem', marginTop: '4px' }}>2</div><div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>6월</div></div>
                            <div style={{ flex: 1, textAlign: 'center' }}><div style={{ height: '10px', background: 'var(--color-warning)' }}></div><div style={{ fontSize: '0.65rem', marginTop: '4px', color: 'var(--color-warning)' }}>1</div><div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>7월</div></div>
                            <div style={{ flex: 1, textAlign: 'center' }}><div style={{ height: '2px', background: 'var(--color-down)' }}></div><div style={{ fontSize: '0.65rem', marginTop: '4px', color: 'var(--color-down)' }}>0</div><div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>8월</div></div>
                            <div style={{ flex: 1, textAlign: 'center' }}><div style={{ height: '2px', background: 'var(--color-down)' }}></div><div style={{ fontSize: '0.65rem', marginTop: '4px', color: 'var(--color-down)' }}>0</div><div style={{ fontSize: '0.65rem', color: 'var(--color-down)' }}>9월</div></div>
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--color-down)', fontWeight: 800, marginTop: '16px', textAlign: 'center' }}>
                            8월 이후 거래 절벽(Transaction Cliff) 현상 확연
                        </div>
                    </div>
                </div>

                {/* 4. AI Insight Box */}
                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', display: 'flex', marginBottom: '40px' }}>
                    <div style={{ flex: 1.5, padding: '40px' }}>
                        <div className="num-font" style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '24px' }}>
                            <div style={{ background: 'var(--color-cyan)', color: 'var(--bg-main)', padding: '2px 8px', fontSize: '0.8rem', fontWeight: 800 }}>◎ AI MARKET INTELLIGENCE ENGINE</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>MODEL: MACRO-ESTATE V4.8 QUANT</div>
                        </div>
                        <h2 style={{ fontSize: '1.6rem', color: 'var(--text-dark)', fontWeight: 800, lineHeight: 1.4, marginBottom: '24px' }}>
                            "현재 아시아선수촌은 <span style={{ color: 'var(--color-down)' }}>'실거래 급락 + 호가 방어'</span> 상태입니다."
                        </h2>
                        <div style={{ fontSize: '1.05rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                            직전 7월 실거래가는 최고점(44.5억원) 대비 <strong style={{ color: 'var(--color-down)' }}>22.4% 하락한 34.5억원</strong>에 체결되었으나, 현재 매도 호가는 <strong style={{ color: 'var(--color-cyan)' }}>41.9억원으로 하락폭이 5.8%</strong>에 불과합니다. 매수자와 매도자의 가격 눈높이가 <strong style={{ color: 'var(--text-dark)' }}>7.4억원</strong> 벌어져 있어 전형적인 거래 절벽 현상이 심화되고 있습니다. 향후 1~2개월 내 매도자의 급매 출현 여부가 송파구 대형 평형 전반의 가격 방향성을 결정짓는 핵심 변곡점이 될 것입니다.
                        </div>
                    </div>
                    <div style={{ flex: 1, borderLeft: '1px solid var(--border-light)', padding: '40px', background: 'rgba(255,255,255,0.01)' }}>
                        <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '24px', letterSpacing: '1px' }}>DIAGNOSTIC TELEMETRY CHECKLIST</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div style={{ display: 'flex', gap: '16px' }}>
                                <div style={{ color: 'var(--color-down)', fontSize: '1.2rem' }}>①</div>
                                <div><div style={{ fontWeight: 800, color: 'var(--text-dark)', fontSize: '0.95rem' }}>가격 괴리율 확대</div><div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--color-down)' }}>+21.4% (선도 50개 단지 중 1위)</div></div>
                            </div>
                            <div style={{ display: 'flex', gap: '16px' }}>
                                <div style={{ color: 'var(--color-warning)', fontSize: '1.2rem' }}>②</div>
                                <div><div style={{ fontWeight: 800, color: 'var(--text-dark)', fontSize: '0.95rem' }}>거래 공백 지속</div><div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--color-warning)' }}>63일간 정상 체결 등록 0건 (매수 실종)</div></div>
                            </div>
                            <div style={{ display: 'flex', gap: '16px' }}>
                                <div style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>③</div>
                                <div><div style={{ fontWeight: 800, color: 'var(--text-dark)', fontSize: '0.95rem' }}>호가 방어선 유지</div><div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>소유주 대다수 41억원 이상 호가 고수</div></div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}
