import React from 'react';
import fs from 'fs';
import path from 'path';
import Sidebar from '../Sidebar';

export const dynamic = 'force-dynamic';

export default async function NewsFactCheckPage() {
    return (
        <div className="app-wrapper">
            <Sidebar activePath="/news" />
            <div className="main-content">
                <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px', fontFamily: 'var(--font-pretendard, sans-serif)' }}>
                    <div style={{ marginBottom: '40px' }}>
                        <h1 style={{ fontSize: '32px', fontWeight: '800', margin: '0 0 8px 0', color: 'var(--text-dark)' }}>🔍 부동산 팩트체크</h1>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '15px' }}>
                            실시간 뉴스의 본문과 헤드라인이 과장되었는지, RealFifty의 팩트 데이터로 철저하게 검증합니다.
                        </p>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        {/* Mockup Fact-Check Item 1 */}
                        <div style={{
                            backgroundColor: 'white',
                            border: '1px solid var(--border-light)',
                            borderRadius: '16px',
                            padding: '32px',
                            boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
                        }}>
                            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
                                <span style={{ backgroundColor: '#ffeaeb', color: '#ba1a1a', padding: '6px 12px', borderRadius: '4px', fontSize: '12px', fontWeight: '800' }}>과장 보도 주의</span>
                                <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>연합뉴스 · 2026-08-10</span>
                                <a href="https://news.google.com" target="_blank" rel="noreferrer" style={{ marginLeft: 'auto', fontSize: '13px', color: '#005fb0', textDecoration: 'none', fontWeight: '700', padding: '6px 12px', border: '1px solid #005fb0', borderRadius: '4px', transition: 'all 0.2s' }}>
                                    원문 기사 읽기 🔗
                                </a>
                            </div>
                            <h2 style={{ fontSize: '22px', fontWeight: '800', marginBottom: '16px', lineHeight: '1.4' }}>
                                📰 기사 헤드라인: "수도권 15억 ~ 20억 아파트 절반 이상 신고가 랠리!"
                            </h2>
                            <div style={{ padding: '16px', backgroundColor: '#fafafa', borderLeft: '4px solid #ddd', marginBottom: '24px', fontSize: '14px', color: '#555', lineHeight: '1.6' }}>
                                <strong>💡 기사 본문 요약:</strong> 최근 1개월간 서울 및 수도권의 15억~20억 매물 중 53.8%가 종전 최고가(ATH)를 뚫고 신고가를 달성했다며, 강남발 상승세가 강북과 수도권 외곽으로 급격히 번지고 있다고 주장함.
                            </div>

                            <div style={{ backgroundColor: '#f5f7fa', padding: '24px', borderRadius: '12px', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '-14px', left: '24px', backgroundColor: '#005fb0', color: 'white', padding: '4px 12px', borderRadius: '4px', fontSize: '13px', fontWeight: '800' }}>
                                    REALFIFTY 데이터 팩트 검증
                                </div>
                                <p style={{ fontSize: '15px', color: '#131b2e', lineHeight: '1.7', marginTop: '10px', marginBottom: 0 }}>
                                    <strong>결론: 기사 본문에 언급된 '강남발 전방위적 신고가 랠리'는 RealFifty 데이터와 완벽히 상구되는 "거짓"에 가깝습니다.</strong>
                                    <br /><br />
                                    기사 본문은 강남구 대장 아파트들의 가격이 폭등하며 주변을 끌어올리고 있다고 묘사했으나,
                                    RealFifty가 1분 단위로 추적 중인 상위 50개 대장 아파트의 312개 세부 평형 데이터를 분석한 결과,
                                    현재 역대 최고가(ATH)에 도달한 평형은 단 <strong>12개(전체의 약 4%)</strong>에 불과합니다.
                                    <br /><br />
                                    오히려 기사에서 상승의 진원지로 지목한 강남 대장주(은마, 선경, 래미안원베일리 등) 국민평형의 일평균 실거래 하락률은 <strong>-14% ~ -21%</strong> 사이를 강력하게 유지하고 있습니다. 본 기사는 거래량이 극히 적은 일부 초소형 아파트나 2026년 신축 입주 단지만을 편향적으로 표본 추출하여 '절반 이상 신고가'라는 통계 착시를 유발한 전형적인 포모(FOMO) 조장 기사로 판단됩니다.
                                </p>
                            </div>
                        </div>

                        {/* Mockup Fact-Check Item 2 */}
                        <div style={{
                            backgroundColor: 'white',
                            border: '1px solid var(--border-light)',
                            borderRadius: '16px',
                            padding: '32px',
                            boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
                        }}>
                            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
                                <span style={{ backgroundColor: '#e8f5e9', color: '#006b54', padding: '6px 12px', borderRadius: '4px', fontSize: '12px', fontWeight: '800' }}>팩트 일치</span>
                                <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>한국경제 · 2026-08-08</span>
                                <a href="https://news.google.com" target="_blank" rel="noreferrer" style={{ marginLeft: 'auto', fontSize: '13px', color: '#005fb0', textDecoration: 'none', fontWeight: '700', padding: '6px 12px', border: '1px solid #005fb0', borderRadius: '4px', transition: 'all 0.2s' }}>
                                    원문 기사 읽기 🔗
                                </a>
                            </div>
                            <h2 style={{ fontSize: '22px', fontWeight: '800', marginBottom: '16px', lineHeight: '1.4' }}>
                                📰 기사 헤드라인: "강남 3구 거래 절벽 심화... 대장주 아파트 썰렁"
                            </h2>
                            <div style={{ padding: '16px', backgroundColor: '#fafafa', borderLeft: '4px solid #ddd', marginBottom: '24px', fontSize: '14px', color: '#555', lineHeight: '1.6' }}>
                                <strong>💡 기사 본문 요약:</strong> 금리 인상과 스트레스 DSR 대출 규제 여파로 강남 3구 랜드마크 단지조차 한 달간 실거래가 2~3건에 머물고 있으며, 매수자와 매도자의 희망 가격 차이가 너무 커서 거래 체결이 이루어지지 않고 있다고 보도함.
                            </div>

                            <div style={{ backgroundColor: '#f5f7fa', padding: '24px', borderRadius: '12px', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '-14px', left: '24px', backgroundColor: '#005fb0', color: 'white', padding: '4px 12px', borderRadius: '4px', fontSize: '13px', fontWeight: '800' }}>
                                    REALFIFTY 데이터 팩트 검증
                                </div>
                                <p style={{ fontSize: '15px', color: '#131b2e', lineHeight: '1.7', marginTop: '10px', marginBottom: 0 }}>
                                    <strong>결론: 완벽한 사실입니다. 본문이 지적한 "매도자와 매수자의 실거래-호가 갭 차이"가 저희 지표에 정확히 잡히고 있습니다.</strong>
                                    <br /><br />
                                    RealFifty 거래량 추적 모듈에 따르면, 잠실 <strong>리센츠 109A</strong>, 대치 <strong>은마 112</strong> 등 거대 단지임에도 최근 30일 실거래가 <strong>단 2건</strong>에 불과합니다.<br /><br />
                                    뿐만 아니라 저희 시스템의 <strong>[실거래-최저호가 갭 분석]</strong> 결과, 아시아선수촌 등 주요 단지는 최근 실거래가 하락폭(-22%)에 비해 최저호가 하락폭(-4%)이 비정상적으로 방어되어, 갭이 18%p에 육박하고 있습니다. 매도자는 호가를 내리지 않고 버티며, 매수자는 폭락가(급매) 수준의 실거래가 아니면 안 산다는 본문의 "평행선 심리 분석"은 현재 RealFifty 데이터 지표와 100% 일치합니다.
                                </p>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
