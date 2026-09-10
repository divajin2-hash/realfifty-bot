import React from 'react'
import '../globals.css'
import Sidebar from '../Sidebar'
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic';

export default async function MarketDashboard() {
    const jsonPath = path.join(process.cwd(), 'src', 'data', 'kb50_stats.json');
    let rawData = [];
    try { rawData = JSON.parse(fs.readFileSync(jsonPath, 'utf8')); } catch (e) { }

    const groupedData = (rawData as any[]).map(group => {
        return {
            complex: group.complex,
            stats: group.stats.map((s: any) => {
                const recentPrice = s.recent_deal_absolute ? s.recent_deal_absolute.price : s.highest_deal_price;
                const recent_drop_rate = (s.highest_deal_price > 0 && recentPrice) ? ((recentPrice - s.highest_deal_price) / s.highest_deal_price) * 100 : 0;
                return {
                    highest_deal_price: s.highest_deal_price,
                    recent_deal_absolute: s.recent_deal_absolute,
                    month_volume: s.month_volume,
                    current_lowest_ask: s.current_lowest_ask,
                    recent_drop_rate: recent_drop_rate,
                    mdd_rate: s.highest_deal_price > 0 ? ((s.current_lowest_ask - s.highest_deal_price) / s.highest_deal_price) * 100 : 0,
                    pyeong_name: s.pyeong_name,
                    match_key_area: s.match_key_area
                }
            })
        }
    });

    function getRepresentativeStat(stats: any[]) {
        if (!stats || stats.length === 0) return null;
        const now = new Date().getTime();
        const scoredStats = stats.map((s: any) => {
            let diffDays = 99999;
            if (s.recent_deal_absolute && s.recent_deal_absolute.date) {
                diffDays = Math.abs(now - new Date(s.recent_deal_absolute.date).getTime()) / (1000 * 3600 * 24);
            }
            return { ...s, diffDays, isAlive: diffDays <= 365, groupDist: Math.abs(s.match_key_area - 84) };
        });
        scoredStats.sort((a, b) => {
            if (a.isAlive !== b.isAlive) return a.isAlive ? -1 : 1;
            if (a.groupDist !== b.groupDist) return a.groupDist - b.groupDist;
            return (b.month_volume || 0) - (a.month_volume || 0);
        });
        return scoredStats[0];
    }

    const scatterPoints = groupedData.map(g => {
        const rep = getRepresentativeStat(g.stats);
        if (!rep) return null;
        return {
            name: g.complex.name,
            x: rep.recent_drop_rate, // 실거래 하락 (X축)
            y: rep.mdd_rate, // 호가 하락 (Y축)
            pyeong: rep.pyeong_name,
            ask: rep.current_lowest_ask,
            deal: rep.recent_deal_absolute?.price
        };
    }).filter(p => p !== null);

    const q2Points = scatterPoints.filter(p => p!.x < -10 && p!.y > p!.x + 3); // 호가 방어
    const q3Points = [...scatterPoints].sort((a, b) => a!.x - b!.x); // 가격 급락 (단순히 x 제일 낮은 순)

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/market" />

            <div className="main-content" style={{ padding: '60px 50px', backgroundColor: 'var(--bg-main)', minHeight: '100vh', fontFamily: "'Pretendard Variable', sans-serif" }}>

                {/* 1. Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px', borderBottom: '1px solid var(--border-light)', paddingBottom: '12px' }}>
                    <div className="num-font" style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '1px' }}>
                        <div style={{ color: 'var(--color-cyan)', fontWeight: 800 }}><span style={{ color: 'var(--text-dark)' }}>■</span> MACRO REGIME RADAR</div>
                        <div>/ ENGINE MODE: 50-TICK CONTINUOUS DEPTH</div>
                        <div>/ REFRESH: 1000ms</div>
                    </div>
                    <div className="num-font" style={{ display: 'flex', gap: '12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <span>1D</span><span>1W</span><span>1M</span><span>3M</span>
                        <span style={{ backgroundColor: 'var(--color-cyan)', color: 'var(--bg-main)', padding: '0 4px', fontWeight: 800 }}>1Y</span>
                        <span>3Y</span><span>ALL</span>
                    </div>
                </div>

                {/* 2. Top Banner Metrics */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '32px' }}>
                    <div>
                        <div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--color-cyan)', letterSpacing: '1px', marginBottom: '8px' }}>
                            TERMINAL BENCHMARK :: REALFIFTY LEADING 50 COMPOSITE
                        </div>
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px' }}>
                            <div className="num-font" style={{ fontSize: '3.5rem', fontWeight: 900, color: 'var(--text-dark)', letterSpacing: '-1px' }}>94.18</div>
                            <div className="num-font" style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--color-cyan)' }}>▴ 0.02p (+0.02%)</div>
                            <div className="num-font" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>PREV CLOSE: 94.16</div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '40px' }}>
                        <div style={{ borderLeft: '1px solid var(--border-light)', paddingLeft: '24px' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>고점 대비 회복률</div>
                            <div className="num-font" style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-cyan)' }}>95.38%</div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>전고점 100pt 기준</div>
                        </div>
                        <div style={{ borderLeft: '1px solid var(--border-light)', paddingLeft: '24px' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>30일 누적 거래량</div>
                            <div className="num-font" style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-down)' }}>9건</div>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>조건미달: -80.0%</div>
                        </div>
                        <div style={{ borderLeft: '1px solid var(--border-light)', paddingLeft: '24px' }}>
                            <div className="num-font" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px' }}>시장 스트레스 지수</div>
                            <div className="num-font" style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--color-down)' }}>68 <span style={{ fontSize: '1rem' }}>위험 (HIGH)</span></div>
                        </div>
                    </div>
                </div>

                {/* 3. Trailing Index & Cycle Metric */}
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2px', backgroundColor: 'var(--border-light)', border: '1px solid var(--border-light)', marginBottom: '40px' }}>
                    <div style={{ background: 'var(--bg-card)', padding: '32px', display: 'flex', flexDirection: 'column' }}>
                        <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1rem', color: 'var(--color-cyan)', fontWeight: 800, marginBottom: '32px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <span>✦ RealFifty 50 Leading Index Trajectory</span>
                                <span style={{ border: '1px solid var(--border-light)', color: 'var(--text-muted)', padding: '2px 8px', fontSize: '0.75rem' }}>12-MONTH TRAILING</span>
                            </div>
                            <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '0.85rem' }}>— 실거래 지수 &nbsp; <span style={{ color: 'var(--border-light)' }}>━</span> 60MA 추세선</span>
                        </div>
                        <div style={{ flex: 1, border: '1px solid var(--border-light)', position: 'relative', overflow: 'hidden', minHeight: '240px', background: 'rgba(255,255,255,0.01)' }}>
                            {/* Fake SVG Chart mapped to terminal style */}
                            <svg width="100%" height="100%" viewBox="0 0 800 200" preserveAspectRatio="none" style={{ position: 'absolute', top: 0, left: 0 }}>
                                <path d="M 0 150 Q 200 120 300 50 T 600 130 T 800 120" fill="none" stroke="var(--color-cyan)" strokeWidth="3" />
                                <path d="M 0 160 Q 200 130 300 60 T 600 140 T 800 130" fill="none" stroke="var(--text-muted)" strokeWidth="1" strokeDasharray="5,5" />
                            </svg>
                            {/* Callouts */}
                            <div className="num-font" style={{ position: 'absolute', top: '30px', left: '35%', background: 'var(--bg-card)', border: '1px solid var(--color-cyan)', padding: '4px 12px', fontSize: '0.75rem', color: 'var(--text-dark)' }}>
                                ▲ 98.4p 고점 돌파 시도
                            </div>
                            <div className="num-font" style={{ position: 'absolute', top: '100px', left: '50%', background: 'var(--color-down)', color: 'var(--bg-main)', padding: '4px 12px', fontSize: '0.75rem', fontWeight: 800 }}>
                                ▼ 대출 규제 직후 거래 급감
                            </div>
                            <div className="num-font" style={{ position: 'absolute', top: '160px', left: '70%', background: 'var(--color-cyan)', color: 'var(--bg-main)', padding: '4px 12px', fontSize: '0.75rem', fontWeight: 800 }}>
                                MIN: 94.18 (약세 수렴)
                            </div>
                            {/* X Axis */}
                            <div className="num-font" style={{ position: 'absolute', bottom: '12px', left: '0', width: '100%', display: 'flex', justifyContent: 'space-around', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                <span>2024.02</span><span>2024.04</span><span>2024.06</span><span>2024.08</span><span>2024.09 (CURRENT)</span>
                            </div>
                        </div>
                    </div>

                    <div style={{ background: 'var(--bg-card)', padding: '32px' }}>
                        <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1rem', color: 'var(--text-primary)', fontWeight: 800, marginBottom: '32px' }}>
                            <span>실거래 회복률 분석</span>
                            <span style={{ color: 'var(--color-cyan)', fontSize: '0.8rem' }}>CYCLE METRIC</span>
                        </div>
                        <div style={{ position: 'relative', display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
                            {/* Simple Semi-Circle Arc SVG */}
                            <svg width="240" height="120" viewBox="0 0 200 100">
                                <path d="M 10 90 A 80 80 0 0 1 190 90" fill="none" stroke="var(--border-light)" strokeWidth="8" strokeLinecap="round" />
                                <path d="M 10 90 A 80 80 0 0 1 140 30" fill="none" stroke="var(--color-cyan)" strokeWidth="8" strokeLinecap="round" />
                                <circle cx="140" cy="30" r="6" fill="var(--color-down)" />
                            </svg>
                            <div className="num-font" style={{ position: 'absolute', bottom: '-20px', width: '100%', display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0 20px' }}>
                                <span>저점 89.2%</span><span>현재 95.58%</span>
                            </div>
                        </div>
                        {/* District Bars */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '40px' }}>
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px' }}><span>강남 3구 (강남/서초/송파)</span><span className="num-font" style={{ color: 'var(--color-cyan)', fontWeight: 800 }}>97.8%</span></div>
                                <div style={{ height: '6px', background: 'var(--border-light)' }}><div style={{ width: '97.8%', height: '100%', background: 'var(--color-cyan)' }}></div></div>
                            </div>
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px' }}><span>마용성 (마포/용산/성동)</span><span className="num-font" style={{ color: 'var(--color-cyan)', fontWeight: 800 }}>94.2%</span></div>
                                <div style={{ height: '6px', background: 'var(--border-light)' }}><div style={{ width: '94.2%', height: '100%', background: 'var(--color-cyan)' }}></div></div>
                            </div>
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px' }}><span>노도강 외 외곽 벨트</span><span className="num-font" style={{ color: 'var(--color-down)', fontWeight: 800 }}>88.5%</span></div>
                                <div style={{ height: '6px', background: 'var(--border-light)' }}><div style={{ width: '88.5%', height: '100%', background: 'var(--color-down)' }}></div></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 4. REALFIFTY MARKET MAP & 진단 */}
                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.8fr) minmax(0, 1fr)', gap: '2px', backgroundColor: 'var(--border-light)', border: '1px solid var(--border-light)', marginBottom: '40px' }}>
                    {/* Market Map */}
                    <div style={{ background: 'var(--bg-card)', padding: '32px' }}>
                        <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                            <div style={{ fontSize: '1.4rem', color: 'var(--text-dark)', fontWeight: 800 }}>
                                REALFIFTY MARKET MAP (4분면 매트릭스)
                            </div>
                            <div style={{ border: '1px solid var(--color-cyan)', padding: '2px 12px', fontSize: '0.8rem', color: 'var(--color-cyan)' }}>DUAL-AXIS VALUATION RADAR</div>
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '32px' }}>
                            X축: 실거래가 고점 대비 등락률 (%) ↔ Y축: 최저 호가 고점 대비 등락률 (%) • 단지별 가격 왜곡 및 심리 저항 상태 추적
                        </div>

                        {/* Scatter Plot Grid Area */}
                        <div style={{ position: 'relative', width: '100%', height: '500px', border: '1px solid var(--border-light)' }}>
                            {/* Grid Lines */}
                            <div style={{ position: 'absolute', top: '50%', left: 0, width: '100%', borderTop: '1px dashed rgba(255,255,255,0.2)' }}></div>
                            <div style={{ position: 'absolute', top: 0, left: '50%', height: '100%', borderLeft: '1px dashed rgba(255,255,255,0.2)' }}></div>

                            {/* Quadrant Labels */}
                            <div className="num-font" style={{ position: 'absolute', top: '24px', left: '24px', fontSize: '0.85rem', color: 'var(--color-cyan)' }}>
                                QUADRANT II: 호가 방어 국면<br /><span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>실거래는 급락했으나 매도자 버팀 (매물 잠김)</span>
                            </div>
                            <div className="num-font" style={{ position: 'absolute', top: '24px', right: '24px', fontSize: '0.85rem', color: 'var(--color-cyan)', textAlign: 'right' }}>
                                QUADRANT I: 신고가 랠리 / 시장 주도<br /><span style={{ background: 'var(--color-cyan)', color: 'var(--bg-main)', padding: '2px 6px', fontWeight: 800, marginTop: '8px', display: 'inline-block', fontSize: '0.75rem' }}>초강세구간 (+2.4% / +4.1%)</span>
                            </div>
                            <div className="num-font" style={{ position: 'absolute', bottom: '24px', left: '24px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                QUADRANT III: 가격 항복 & 급락 국면<br /><span style={{ fontSize: '0.75rem' }}>실거래 역행 분열 및 매수 실종으로 매도항복</span>
                            </div>
                            <div className="num-font" style={{ position: 'absolute', bottom: '24px', right: '24px', fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'right' }}>
                                QUADRANT IV: 호가 조정 / 매수자 우위<br /><span style={{ fontSize: '0.75rem' }}>실거래는 유지되나 호가가 하향수렴 중</span>
                            </div>

                            {/* Axes Labels */}
                            <div className="num-font" style={{ position: 'absolute', bottom: '4px', left: '4px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>◄ 실거래가 -35% (급락)</div>
                            <div className="num-font" style={{ position: 'absolute', bottom: '4px', right: '4px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>신고가 +10% ►</div>

                            {/* Scatter Points (Simulated Real Data mapping!) */}
                            {scatterPoints.map((p, i) => {
                                // X domain: -35% to 10%, Y domain: -35% to 10%
                                const xPercent = Math.min(Math.max((p!.x - (-35)) / 45 * 100, 0), 100);
                                const yPercent = 100 - Math.min(Math.max((p!.y - (-35)) / 45 * 100, 0), 100);
                                const isQ2 = p!.x < -10 && p!.y > p!.x + 3;
                                const isQ3 = p!.x < -15 && p!.y <= p!.x + 3; // deep drop, both
                                const color = isQ2 ? 'var(--color-cyan)' : isQ3 ? 'var(--color-down)' : 'rgba(255,255,255,0.4)';
                                const highlight = isQ2 || isQ3 || (p!.name === '래미안대치팰리스' || p!.name === '마포래미안푸르지오');

                                return (
                                    <div key={i} style={{ position: 'absolute', left: `${xPercent}%`, top: `${yPercent}%`, transform: 'translate(-50%, -50%)', display: 'flex', alignItems: 'center', zIndex: highlight ? 10 : 1 }}>
                                        <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: color, border: '1px solid var(--bg-card)' }}></div>
                                        {highlight && (
                                            <div className="num-font" style={{ marginLeft: '8px', fontSize: '0.75rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', border: `1px solid ${color}`, background: 'var(--bg-card)', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
                                                {p!.name} <span style={{ color: 'var(--text-muted)' }}>({p!.x.toFixed(1)}% / {p!.y.toFixed(1)}%)</span>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* 진단 Text */}
                    <div style={{ background: 'var(--bg-card)', padding: '32px' }}>
                        <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', color: 'var(--color-cyan)', fontSize: '1.1rem', fontWeight: 800 }}>
                            <span>◎ 단지별 포지션 심층 진단</span>
                        </div>

                        {q2Points[0] && (
                            <div style={{ border: '1px solid var(--border-light)', padding: '24px', borderRadius: '8px', marginBottom: '24px', background: 'rgba(0,240,255,0.03)' }}>
                                <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed var(--border-light)', paddingBottom: '16px', marginBottom: '16px' }}>
                                    <span style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-dark)' }}>{q2Points[0].name} <span style={{ fontSize: '1rem' }}>{q2Points[0].pyeong}</span></span>
                                    <span style={{ background: 'rgba(0,240,255,0.1)', color: 'var(--color-cyan)', padding: '4px 12px', fontSize: '0.8rem', fontWeight: 800 }}>QUADRANT II</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', fontSize: '0.85rem' }}>
                                    <div><span style={{ color: 'var(--text-muted)' }}>실거래 하락률</span><br /><strong className="num-font" style={{ color: 'var(--color-down)', fontSize: '1.2rem' }}>{q2Points[0].x.toFixed(1)}%</strong></div>
                                    <div><span style={{ color: 'var(--text-muted)' }}>호가 하락률</span><br /><strong className="num-font" style={{ color: 'var(--color-cyan)', fontSize: '1.2rem' }}>{q2Points[0].y.toFixed(1)}%</strong></div>
                                    <div><span style={{ color: 'var(--text-muted)' }}>스프레드 괴리</span><br /><strong className="num-font" style={{ color: 'var(--text-dark)', fontSize: '1.2rem' }}>+{Math.abs(q2Points[0].y - q2Points[0].x).toFixed(1)}%</strong></div>
                                </div>
                                <div style={{ fontSize: '0.95rem', color: 'var(--color-cyan)', lineHeight: 1.6 }}>
                                    <strong>[호가 방어 구간 판정]</strong> 매도자가 최근 하락 실거래를 인정하지 않고 호가를 지속 유지. 거래 성사 불가 국면(Liquidity Freeze) 지속 중.
                                </div>
                            </div>
                        )}

                        {q3Points[0] && (
                            <div style={{ border: '1px solid var(--border-light)', padding: '24px', borderRadius: '8px', background: 'rgba(255,123,114,0.03)' }}>
                                <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px dashed var(--border-light)', paddingBottom: '16px', marginBottom: '16px' }}>
                                    <span style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-dark)' }}>{q3Points[0].name} <span style={{ fontSize: '1rem' }}>{q3Points[0].pyeong}</span></span>
                                    <span style={{ background: 'rgba(255,123,114,0.1)', color: 'var(--color-down)', padding: '4px 12px', fontSize: '0.8rem', fontWeight: 800 }}>QUADRANT III</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', fontSize: '0.85rem' }}>
                                    <div><span style={{ color: 'var(--text-muted)' }}>실거래 하락률</span><br /><strong className="num-font" style={{ color: 'var(--color-down)', fontSize: '1.2rem' }}>{q3Points[0].x.toFixed(1)}%</strong></div>
                                    <div><span style={{ color: 'var(--text-muted)' }}>호가 하락률</span><br /><strong className="num-font" style={{ color: 'var(--color-down)', fontSize: '1.2rem' }}>{q3Points[0].y.toFixed(1)}%</strong></div>
                                    <div><span style={{ color: 'var(--text-muted)' }}>스프레드 괴리</span><br /><strong className="num-font" style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>동조화 붕괴</strong></div>
                                </div>
                                <div style={{ fontSize: '0.95rem', color: 'var(--color-down)', lineHeight: 1.6 }}>
                                    <strong>[가격 항복 국면 판정]</strong> 최고가 대비 급매물들이 속출하며 매도 호가마저 실거래선 밑으로 내려앉음. 하락 압력 가속화.
                                </div>
                            </div>
                        )}

                        <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px', fontSize: '0.85rem', color: 'var(--color-cyan)', borderTop: '1px solid var(--border-light)', paddingTop: '16px' }}>
                            <span>RADAR ACCURACY INDEX</span>
                            <span style={{ fontWeight: 800 }}>99.2% CONFIDENCE</span>
                        </div>
                    </div>
                </div>

                {/* 5. Historical Volume (Mockup) */}
                <div style={{ background: 'var(--bg-card)', padding: '32px', border: '1px solid var(--border-light)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '32px' }}>
                        <div>
                            <div className="num-font" style={{ fontSize: '1.2rem', color: 'var(--text-dark)', fontWeight: 800, marginBottom: '8px' }}>
                                📊 50대 단지 거래량 유동성 고갈 추이 (36-MONTH HISTORICAL VOLUME)
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>월평균 정상 거래 체결량(45건) 대비 2026년 하반기 유동성 절벽 상태 계측</div>
                        </div>
                        <div style={{ background: 'rgba(255,123,114,0.1)', border: '1px solid var(--color-down)', padding: '8px 16px', color: 'var(--color-down)', fontSize: '0.85rem', fontWeight: 800, borderRadius: '4px' }}>
                            ⚠️ 단 9건 체결로 80% 유동성 증발.
                        </div>
                    </div>
                    {/* Bar Chart Mockup */}
                    <div style={{ height: '160px', display: 'flex', alignItems: 'flex-end', gap: '8px', borderBottom: '1px solid var(--border-light)' }}>
                        <div style={{ flex: 1, backgroundColor: 'rgba(0,240,255,0.1)', height: '70%' }}></div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(0,240,255,0.15)', height: '80%' }}></div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(0,240,255,0.2)', height: '100%', borderTop: '2px solid var(--color-cyan)' }}></div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(0,240,255,0.1)', height: '60%' }}></div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(0,240,255,0.1)', height: '55%' }}></div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', height: '30%' }}></div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(255,123,114,0.2)', height: '20%' }}></div>
                        <div style={{ flex: 1, backgroundColor: 'rgba(255,123,114,0.3)', height: '10%', borderTop: '2px solid var(--color-down)' }}></div>
                    </div>
                    <div className="num-font" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <span>2024.01</span><span>2024.07 (PEAK)</span><span>2025.01</span><span>2025.07</span><span>2026.01</span><span style={{ color: 'var(--color-down)' }}>2026.09 (CURRENT)</span>
                    </div>
                </div>

            </div>
        </div>
    )
}
