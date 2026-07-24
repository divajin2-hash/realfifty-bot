import React from 'react'
import './globals.css'
import ClientGrid from './ClientGrid'
import SearchInput from './SearchInput'
import TickerClient from './TickerClient'
import rawData from '../data/kb50_stats.json'

export const revalidate = 60;

export default async function Dashboard() {

    const groupedData = (rawData as any[]).map(group => {
        return {
            complex: group.complex,
            stats: group.stats.map((s: any) => {
                const recentPrice = s.recent_deal_absolute ? s.recent_deal_absolute.price : s.highest_deal_price;
                // 최고가 대비 "최근 실거래가" 하락률
                const recent_drop_rate = (s.highest_deal_price > 0 && recentPrice) ? -Math.abs(((s.highest_deal_price - recentPrice) / s.highest_deal_price) * 100) : 0;
                return {
                    id: group.complex.id + s.match_key_area,
                    match_key_area: s.match_key_area,
                    highest_deal_price: s.highest_deal_price,
                    highest_deal_date: s.highest_deal_date,
                    recent_deal_absolute: s.recent_deal_absolute,
                    month_deals: s.month_deals,
                    month_volume: s.month_volume,
                    volume_drop_rate: s.volume_drop_rate,
                    current_lowest_ask: s.current_lowest_ask,
                    recent_drop_rate: recent_drop_rate,
                    mdd_rate: s.highest_deal_price > 0 ? -Math.abs(((s.highest_deal_price - s.current_lowest_ask) / s.highest_deal_price) * 100) : 0
                }
            })
        }
    });

    // 대표평형 추출 로직 (UI 표출 기준)
    function getRepresentativeStat(stats: any[]) {
    if (!stats || stats.length === 0) return null;
    const now = new Date().getTime();
    
    const scoredStats = stats.map((s: any) => {
        let diffDays = 99999;
        if (s.recent_deal_absolute && s.recent_deal_absolute.date) {
            const lastDate = new Date(s.recent_deal_absolute.date).getTime();
            diffDays = Math.abs(now - lastDate) / (1000 * 3600 * 24);
        }
        const dist84 = Math.abs(s.match_key_area - 84);
        const isAlive = diffDays <= 365;
        const groupDist = (s.match_key_area >= 82 && s.match_key_area <= 85) ? 0 : dist84;
        
        return { ...s, diffDays, dist84, isAlive, groupDist };
    });
    
    scoredStats.sort((a, b) => {
        if (a.isAlive !== b.isAlive) return a.isAlive ? -1 : 1;
        if (a.groupDist !== b.groupDist) return a.groupDist - b.groupDist;
        return b.highest_deal_price - a.highest_deal_price;
    });
    
    return scoredStats[0];
}

    // 기획자님 지시: 화면에 노출되는 '대표평형' 기준으로 고점대비 실거래가가 가장 낮은 순(하락폭이 큰 순) 정렬!
    groupedData.sort((a, b) => {
        const repA = getRepresentativeStat(a.stats);
        const repB = getRepresentativeStat(b.stats);

        // 유효하면 하락률 반환, 없으면 0. 가장 낮은 값(큰 마이너스 값)이 1등
        const dropA = repA ? repA.recent_drop_rate : 0;
        const dropB = repB ? repB.recent_drop_rate : 0;

        return dropA - dropB; // 오름차순 (예: -38%가 -10%보다 먼저 배열됨)
    });
    groupedData.forEach((g: any, idx: number) => g.rank = idx + 1);

    // 전체 단지 평균 실거래 하락률 (진짜 표출된 대표평형들 기준)
    const totalDropRates = groupedData.map(g => {
        const rep = getRepresentativeStat(g.stats);
        return rep ? rep.recent_drop_rate : null;
    }).filter(v => v !== null) as number[];

    const avgDrop = totalDropRates.length > 0
        ? (totalDropRates.reduce((acc, val) => acc + val, 0) / totalDropRates.length).toFixed(2)
        : '0.00';


    
    return (
        <div className="app-wrapper">
            {/* 🔴 Left Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-logo" style={{ padding: '32px 24px 12px 24px' }}>
                    <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                        Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
                    </div>
                    
                </div>
                <div className="sidebar-menu" style={{ marginTop: '10px' }}>
                    <div className="menu-item active">📈 실시간 시장 현황</div>
                    <div className="menu-item">📊 거래량 추이 통계</div>
                    <div className="menu-item">🔔 급매물 알림</div>
                    <div className="menu-item">💼 관심 단지 등록</div>
                </div>
                <div style={{ marginTop: 'auto', padding: '24px' }}>
                    <SearchInput />
                    <div style={{ backgroundColor: '#ba1a1a', padding: '12px', textAlign: 'center', borderRadius: '4px', color: 'white', fontWeight: 'bold', cursor: 'pointer' }}>
                        종합 마켓 리포트
                    </div>
                </div>
            </aside>

            {/* 🔵 Main Content */}
            <div className="main-content">
                <TickerClient items={(() => {
                    const avgNum = parseFloat(avgDrop);
                    const items = groupedData.map(g => {
                        const rep = getRepresentativeStat(g.stats);
                        return {
                            name: g.complex.name,
                            rawDrop: rep ? rep.recent_drop_rate : 0,
                            drop: rep ? rep.recent_drop_rate.toFixed(1) : "0.0",
                            isSevere: rep && rep.recent_drop_rate <= -20,
                            rank: 0
                        };
                    });
                    
                    // Filter: Only include items whose drop is WORSE (more negative) than the average drop
                    const filtered = items.filter(item => item.rawDrop < avgNum);
                    
                    // Assign explicit ranking (since groupedData is already sorted)
                    filtered.forEach((item, idx) => {
                        item.rank = idx + 1;
                    });
                    
                    return filtered;
                })()} />

                <div className="dashboard-area">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-1px' }}>선도50 아파트 모니터링</h1>
                            <p style={{ color: '#76777d', fontSize: '1rem', marginTop: '12px' }}>
                                총 {groupedData.length}개 단지 추적 중 | <strong style={{ color: '#ba1a1a' }}>최고가 대비 실거래가 하락률(MDD)</strong> 낮은 순 정렬
                            </p>
                        </div>

                        <div style={{ display: 'flex', gap: '16px' }}>
                            <div style={{ backgroundColor: '#e6e8eb', padding: '16px 24px', borderRadius: '8px', minWidth: '160px' }}>
                                <div style={{ fontSize: '0.8rem', color: '#76777d', fontWeight: 700 }}>대표평형 평균 하락률</div>
                                <div className="num-font" style={{ fontSize: '2rem', color: '#ba1a1a', fontWeight: 800 }}>{avgDrop}%</div>
                            </div>
                            <div style={{ backgroundColor: '#e6e8eb', padding: '16px 24px', borderRadius: '8px', minWidth: '160px' }}>
                                <div style={{ fontSize: '0.8rem', color: '#76777d', fontWeight: 700 }}>시장 투자 심리</div>
                                <div style={{ fontSize: '2rem', color: '#ba1a1a', fontWeight: 800 }}>약세장(Bearish)</div>
                            </div>
                        </div>
                    </div>

                    <ClientGrid groupedData={groupedData} />
                </div>
            </div>
        </div>
    )
}
