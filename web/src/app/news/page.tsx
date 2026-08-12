import React from 'react';
import fs from 'fs';
import path from 'path';
import Sidebar from '../Sidebar';

export const dynamic = 'force-dynamic';

export default async function NewsFactCheckPage() {
    const newsPath = path.join(process.cwd(), 'src', 'data', 'latest_news.json');
    let newsData: any[] = [];
    try {
        newsData = JSON.parse(fs.readFileSync(newsPath, 'utf8'));
    } catch (e) { }

    return (
        <div className="app-wrapper">
            <Sidebar activePath="/news" />
            <div className="main-content">
                <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px', fontFamily: 'var(--font-pretendard, sans-serif)' }}>
                    <div style={{ marginBottom: '40px' }}>
                        <h1 style={{ fontSize: '32px', fontWeight: '800', margin: '0 0 8px 0', color: 'var(--text-dark)' }}>🔍 부동산 팩트체크</h1>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '15px' }}>
                            실시간 뉴스의 헤드라인이 과장되었는지, RealFifty의 팩트 데이터로 철저하게 검증합니다.
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
                            </div>
                            <h2 style={{ fontSize: '22px', fontWeight: '800', marginBottom: '24px', lineHeight: '1.4' }}>
                                📰 기사 헤드라인: "수도권 15억 ~ 20억 아파트 절반 이상 신고가 랠리!"
                            </h2>

                            <div style={{ backgroundColor: '#f5f7fa', padding: '24px', borderRadius: '12px', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '-14px', left: '24px', backgroundColor: '#005fb0', color: 'white', padding: '4px 12px', borderRadius: '4px', fontSize: '13px', fontWeight: '800' }}>
                                    REALFIFTY 팩트 검증
                                </div>
                                <p style={{ fontSize: '15px', color: '#131b2e', lineHeight: '1.7', marginTop: '10px', marginBottom: 0 }}>
                                    <strong>결론: 절반 이상 신고가는 데이터상 "거짓"에 가깝습니다. 극히 일부 단지의 일시적 현상입니다.</strong>
                                    <br /><br />
                                    RealFifty가 추적 중인 수도권 최상위 50개 대장 아파트의 312개 세부 평형 데이터를 분석한 결과,
                                    현재 역대 최고가(ATH)를 경신하거나 근접한 평형은 <strong>전체의 4% 수준(약 12개 평형)</strong>에 불과합니다.
                                    오히려 대장주 국민평형(84㎡)의 단순 평균 하락률은 <strong>-8.15%</strong>로, 대다수 아파트가 2021년 고점 대비 15~20% 할인을 유지하고 있습니다.<br /><br />
                                    기사에 언급된 '절반 이상'이라는 통계는 특정 지역의 초소형 아파트나 2026년 신축 입주단지만을 편향적으로 표본 추출하여
                                    착시를 일으킨 것으로 강력히 추정됩니다. 불안감에 휩쓸려 추격 매수하기보다는 현재의 객관적 하락장 박스권(-8% 대)을 인지하는 것이 중요합니다.
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
                            </div>
                            <h2 style={{ fontSize: '22px', fontWeight: '800', marginBottom: '24px', lineHeight: '1.4' }}>
                                📰 기사 헤드라인: "강남 3구 거래 절벽 심화... 대장주 아파트 한 달간 2~3건 거래에 그쳐"
                            </h2>

                            <div style={{ backgroundColor: '#f5f7fa', padding: '24px', borderRadius: '12px', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '-14px', left: '24px', backgroundColor: '#005fb0', color: 'white', padding: '4px 12px', borderRadius: '4px', fontSize: '13px', fontWeight: '800' }}>
                                    REALFIFTY 팩트 검증
                                </div>
                                <p style={{ fontSize: '15px', color: '#131b2e', lineHeight: '1.7', marginTop: '10px', marginBottom: 0 }}>
                                    <strong>결론: 완벽한 사실입니다. 매수자와 매도자의 극심한 눈치싸움이 지표로 확인됩니다.</strong>
                                    <br /><br />
                                    RealFifty 거래량 추적 모듈에 따르면, 강남 최상급지 대장 아파트들의 최근 30일간 거래량은 처참한 수준입니다.
                                    예를 들어 잠실 <strong>리센츠 109A</strong> 평형과 강남 <strong>디에이치퍼스티어아이파크 111C</strong> 평형 모두 거대한 단지 규모에도 불구하고
                                    최근 1개월 동안 <strong>단 2건</strong>의 실거래만 등재되었습니다.<br /><br />
                                    이는 최고가 대비 낮은 가격에 던지지 않으려는 매도자의 버티기와, 지금 가격으론 절대 사지 않겠다는 매수자의 스탠스가
                                    정확히 팽팽하게 평행선을 달리고 있다는 것을 의미합니다. 거래 침체기에는 성급한 진입을 삼가는 것이 유리합니다.
                                </p>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
