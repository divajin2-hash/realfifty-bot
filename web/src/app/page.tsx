import React from 'react'
import './globals.css'
import ClientGrid from './ClientGrid'
import SearchInput from './SearchInput'
import TickerClient from './TickerClient'
import Link from 'next/link'
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic';

export default async function Dashboard({ searchParams }: { searchParams: { sort?: string } }) {
    const jsonPath = path.join(process.cwd(), 'src', 'data', 'kb50_stats.json');
    const rawData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

    const groupedData = (rawData as any[]).map(group => {
        return {
            complex: group.complex,
            stats: group.stats.map((s: any) => {
                const recentPrice = s.recent_deal_absolute ? s.recent_deal_absolute.price : s.highest_deal_price;
                // 理쒓퀬媛 ?鍮?"理쒓렐 ?ㅺ굅?섍?" ?섎씫瑜?
                const recent_drop_rate = (s.highest_deal_price > 0 && recentPrice) ? ((recentPrice - s.highest_deal_price) / s.highest_deal_price) * 100 : 0;
                return {
                    id: group.complex.id + s.match_key_area,
                    match_key_area: s.match_key_area,
                    pyeong_name: s.pyeong_name,
                    highest_deal_price: s.highest_deal_price,
                    highest_deal_date: s.highest_deal_date,
                    recent_deal_absolute: s.recent_deal_absolute,
                    month_deals: s.month_deals,
                    month_volume: s.month_volume,
                    volume_drop_rate: s.volume_drop_rate,
                    current_lowest_ask: s.current_lowest_ask,
                    recent_drop_rate: recent_drop_rate,
                    mdd_rate: s.highest_deal_price > 0 ? ((s.current_lowest_ask - s.highest_deal_price) / s.highest_deal_price) * 100 : 0
                }
            })
        }
    });

    // ??쒗룊??異붿텧 濡쒖쭅 (UI ?쒖텧 湲곗?)
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
            // 1. 1????嫄곕옒媛 ?덉뿀???됲삎???곕? (理쒓렐 嫄곕옒 ?쒖꽦??
            if (a.isAlive !== b.isAlive) return a.isAlive ? -1 : 1;

            // 2. 84??(援???됲삎)??媛源뚯슫 寃껋쓣 ?곗꽑 (1?쒖쐞)
            if (a.groupDist !== b.groupDist) return a.groupDist - b.groupDist;

            // 3. 84?↔? ?꾨땲嫄곕굹 嫄곕━媛 媛숇떎硫? 嫄곕옒?됱씠 媛??留롮?(?뺣룄?곸씤) ?됲삎???곗꽑 (2?쒖쐞)
            // max_month_volume? ?대떦 ?됲삎????궗???붽컙 理쒕? 嫄곕옒?됱씠誘濡??몃????쒖꽦?꾨? 媛?????蹂??
            const volA = a.max_month_volume || 0;
            const volB = b.max_month_volume || 0;
            if (volA !== volB) return volB - volA;

            // 4. 留덉?留?蹂대（??理쒓퀬媛 湲곗? ?뺣젹
            return b.highest_deal_price - a.highest_deal_price;
        });

        return scoredStats[0];
    }

    const sortMethod = (await searchParams)?.sort || 'real_drop_high';

    // ?뺣젹 諛⑹떇 ?ㅼ젙
    groupedData.sort((a, b) => {
        const repA = getRepresentativeStat(a.stats);
        const repB = getRepresentativeStat(b.stats);

        const realDropA = repA ? repA.recent_drop_rate : 0;
        const realDropB = repB ? repB.recent_drop_rate : 0;

        const askDropA = repA ? repA.mdd_rate : 0;
        const askDropB = repB ? repB.mdd_rate : 0;

        if (sortMethod === 'real_drop_less') {
            return realDropB - realDropA; // ?ㅺ굅?섍? ?섎씫瑜??곸? ??(?대┝李⑥닚, ?? 0% -> -10% -> -30%)
        } else if (sortMethod === 'ask_drop_high') {
            return askDropA - askDropB; // 理쒖??멸? ?섎씫瑜??믪? ??(?ㅻ쫫李⑥닚, ?? -30% -> -10% -> 0%)
        } else if (sortMethod === 'ask_drop_less') {
            return askDropB - askDropA; // 理쒖??멸? ?섎씫瑜??곸? ??(?대┝李⑥닚)
        } else {
            // 湲곕낯媛? real_drop_high
            return realDropA - realDropB; // ?ㅺ굅?섍? ?섎씫瑜??믪? ??(?ㅻ쫫李⑥닚)
        }
    });
    groupedData.forEach((g: any, idx: number) => g.rank = idx + 1);

    // ?꾩껜 ?⑥? ?됯퇏 ?ㅺ굅?섍? ?섎씫瑜?(吏꾩쭨 異붿텧????쒗룊?뺣뱾 湲곗?)
    const totalDropRates = groupedData.map(g => {
        const rep = getRepresentativeStat(g.stats);
        return rep ? rep.recent_drop_rate : null;
    }).filter(v => v !== null) as number[];

    const avgDrop = totalDropRates.length > 0
        ? (totalDropRates.reduce((acc, val) => acc + val, 0) / totalDropRates.length).toFixed(2)
        : '0.00';

    // ?꾩껜 ?⑥? ?됯퇏 理쒖??멸? ?섎씫瑜?
    const totalAskDropRates = groupedData.map(g => {
        const rep = getRepresentativeStat(g.stats);
        return rep ? rep.mdd_rate : null; // mdd_rate??理쒓퀬媛 ?鍮??꾩옱 理쒖??멸? ?섎씫瑜좎엯?덈떎.
    }).filter(v => v !== null) as number[];

    const avgAskDrop = totalAskDropRates.length > 0
        ? (totalAskDropRates.reduce((acc, val) => acc + val, 0) / totalAskDropRates.length).toFixed(2)
        : '0.00';

    // ?쒖옣 ?ъ옄 ?щ━ 寃곗젙
    const numAvgDrop = parseFloat(avgDrop);
    let marketSentiment = "?쎌꽭??;
    let marketColor = "#005fb0";
    if (numAvgDrop >= 0) {
        marketSentiment = "?곸듅??;
        marketColor = "#ba1a1a";
    } else if (numAvgDrop < -10) {
        marketSentiment = "?섎씫??;
        marketColor = "#005fb0";
    }

    return (
        <div className="app-wrapper">
            {/* ?뵶 Left Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-logo" style={{ padding: '32px 24px 12px 24px' }}>
                    <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                        Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
                    </div>

                </div>
                <div className="sidebar-menu" style={{ marginTop: '10px' }}>
                    <div className="menu-item active">?뱢 ?ㅼ떆媛??쒖옣 ?꾪솴</div>
                    <div className="menu-item">?뱤 嫄곕옒??異붿씠 ?듦퀎</div>
                    <div className="menu-item">?뵒 湲됰ℓ臾??뚮┝</div>
                    <div className="menu-item">?뮳 愿???⑥? ?깅줉</div>
                </div>
                <div style={{ marginTop: 'auto', padding: '24px' }}>
                    <SearchInput />
                    <Link href="/reports" style={{ display: 'block', backgroundColor: 'var(--ticker-red)', padding: '12px', textAlign: 'center', borderRadius: '4px', color: 'white', fontWeight: 'bold', cursor: 'pointer', textDecoration: 'none' }}>종합 마켓 리포트</Link>
                </div>
            </aside>

            {/* ?뵷 Main Content */}
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
                            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-1px' }}>?좊룄50 ?꾪뙆??紐⑤땲?곕쭅</h1>
                            <p style={{ color: '#76777d', fontSize: '1rem', marginTop: '12px' }}>
                                珥?{groupedData.length}媛??⑥? 異붿쟻 以?
                            </p>
                            <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                                <a href="?sort=real_drop_high" style={{ padding: '6px 12px', fontSize: '0.9rem', borderRadius: '4px', textDecoration: 'none', backgroundColor: sortMethod === 'real_drop_high' ? '#2e2f32' : '#e6e8eb', color: sortMethod === 'real_drop_high' ? 'white' : '#2e2f32' }}>?ㅺ굅?섍? ?섎씫 ??????/a>
                                <a href="?sort=real_drop_less" style={{ padding: '6px 12px', fontSize: '0.9rem', borderRadius: '4px', textDecoration: 'none', backgroundColor: sortMethod === 'real_drop_less' ? '#2e2f32' : '#e6e8eb', color: sortMethod === 'real_drop_less' ? 'white' : '#2e2f32' }}>?ㅺ굅?섍? ?섎씫 ???곸? ??/a>
                                <a href="?sort=ask_drop_high" style={{ padding: '6px 12px', fontSize: '0.9rem', borderRadius: '4px', textDecoration: 'none', backgroundColor: sortMethod === 'ask_drop_high' ? '#2e2f32' : '#e6e8eb', color: sortMethod === 'ask_drop_high' ? 'white' : '#2e2f32' }}>理쒖??멸? ?섎씫 ??????/a>
                                <a href="?sort=ask_drop_less" style={{ padding: '6px 12px', fontSize: '0.9rem', borderRadius: '4px', textDecoration: 'none', backgroundColor: sortMethod === 'ask_drop_less' ? '#2e2f32' : '#e6e8eb', color: sortMethod === 'ask_drop_less' ? 'white' : '#2e2f32' }}>理쒖??멸? ?섎씫 ???곸? ??/a>
                            </div>
                        </div>

                        <div style={{ display: 'flex', gap: '16px' }}>
                            <div style={{ backgroundColor: '#e6e8eb', padding: '16px 24px', borderRadius: '8px', minWidth: '220px' }}>
                                <div style={{ fontSize: '0.8rem', color: '#76777d', fontWeight: 700 }}>?됯퇏 ?ㅺ굅?섍? / 理쒖??멸?</div>
                                <div className="num-font" style={{ fontSize: '1.2rem', color: parseFloat(avgDrop) > 0 ? '#ba1a1a' : '#005fb0', fontWeight: 800, marginTop: '4px' }}>
                                    ?ㅺ굅?섍? ?깅씫瑜?{avgDrop}% {parseFloat(avgDrop) > 0 ? '?곸듅' : '?섎씫'}
                                </div>
                                <div className="num-font" style={{ fontSize: '1.2rem', color: parseFloat(avgAskDrop) > 0 ? '#ba1a1a' : '#005fb0', fontWeight: 800, marginTop: '4px' }}>
                                    理쒖??멸? ?깅씫瑜?{avgAskDrop}% {parseFloat(avgAskDrop) > 0 ? '?곸듅' : '?섎씫'}
                                </div>
                            </div>
                            <div
                                style={{ backgroundColor: '#e6e8eb', padding: '16px 24px', borderRadius: '8px', minWidth: '160px', cursor: 'help' }}
                                title="* ?쒖옣 湲곗? ?덈궡: 0% ?댁긽(?곸듅??, 0 ~ -10%(?쎌꽭??, -10% 誘몃쭔(?섎씫??"
                            >
                                <div style={{ fontSize: '0.8rem', color: '#76777d', fontWeight: 700 }}>?쒖옣 ?ъ옄 ?щ━ <span style={{ fontSize: '0.6rem' }}>??/span></div>
                                <div style={{ fontSize: '2rem', color: marketColor, fontWeight: 800 }}>{marketSentiment}</div>
                            </div>
                        </div>
                    </div>

                    <ClientGrid groupedData={groupedData} />
                </div>
            </div>
        </div>
    )
}
