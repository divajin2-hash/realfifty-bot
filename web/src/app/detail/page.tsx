"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, ArrowLeft, ArrowRight, Home } from "lucide-react";
import Link from 'next/link';

export default function ComplexDetail() {
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        // 실제 운영 환경에서는 API를 찌르겠지만, 프로토타입 확인용 JSON을 읽어옵니다.
        fetch('/heliocity_10y_multi.json')
            .then(res => res.json())
            .then(json => setData(json));
    }, []);

    const formatPrice = (price: number) => {
        if (!price) return "정보 없음";
        const eok = Math.floor(price / 100000000);
        const man = Math.floor((price % 100000000) / 10000);
        if (eok === 0) return `${man.toLocaleString()}만`;
        if (man === 0) return `${eok}억`;
        return `${eok}억 ${man.toLocaleString()}`;
    };

    if (!data) {
        return <div className="min-h-screen bg-[#0B0F19] flex items-center justify-center text-white">Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-[#0B0F19] text-white selection:bg-blue-500/30 font-sans p-4 md:p-8 lg:p-16">
            <div className="max-w-7xl mx-auto space-y-12">

                {/* 헤더 및 네비게이션 */}
                <header className="space-y-6">
                    <Link href="/" className="inline-flex items-center text-white/40 hover:text-white transition-colors text-sm font-medium">
                        <ArrowLeft size={16} className="mr-2" />
                        메인 랭킹으로 돌아가기
                    </Link>

                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-8">
                        <div>
                            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                                <span className="px-4 py-1.5 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-semibold border border-indigo-500/20 mb-4 inline-block">
                                    단지 상세 분석 리포트
                                </span>
                            </motion.div>
                            <motion.h1
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="text-4xl md:text-5xl font-extrabold tracking-tight"
                            >
                                {data.complexName}
                            </motion.h1>
                        </div>
                        <p className="text-white/40 text-sm">
                            ※ 평형별 거래 유동성 및 하락장 방어력 비교
                        </p>
                    </div>
                </header>

                {/* 3가지 평형 분석 카드 (Grid) */}
                <div className="grid gap-6 md:grid-cols-3">
                    {Object.keys(data.sizes).map((sizeKey, idx) => {
                        const sizeData = data.sizes[sizeKey];
                        const mdd = ((sizeData.current_ask - sizeData.ath.price) / sizeData.ath.price) * 100;
                        const isDrop = mdd < 0;
                        const badgeColor = isDrop ? "text-blue-400 bg-blue-500/10 border-blue-500/20" : "text-red-400 bg-red-500/10 border-red-500/20";

                        return (
                            <motion.div
                                key={sizeKey}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 * idx }}
                                className="relative p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md overflow-hidden hover:bg-white/10 transition-colors"
                            >
                                {/* 카드 배경 오로라 */}
                                <div className={`absolute -right-20 -top-20 w-48 h-48 rounded-full blur-3xl opacity-20 ${sizeKey === '84' ? 'bg-indigo-500' : 'bg-white'}`} />

                                <div className="relative z-10">
                                    <div className="flex items-center space-x-3 mb-6">
                                        <div className={`p-2 rounded-lg ${sizeKey === '84' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-white/10 text-white/60'}`}>
                                            <Home size={20} />
                                        </div>
                                        <h2 className="text-xl font-bold">{sizeData.label}</h2>
                                    </div>

                                    {/* 수치 비교 영역 */}
                                    <div className="space-y-4 mb-8">
                                        <div className="flex justify-between items-end border-b border-white/5 pb-4">
                                            <div>
                                                <p className="text-xs text-white/40 font-medium mb-1">역대 최고가</p>
                                                <p className="text-[10px] text-white/20 bg-white/5 inline-block px-1.5 py-0.5 rounded">'{sizeData.ath.date}</p>
                                            </div>
                                            <p className="text-xl font-bold">{formatPrice(sizeData.ath.price)}</p>
                                        </div>

                                        <div className="flex justify-between items-center border-b border-white/5 pb-4">
                                            <p className="text-xs text-white/40 font-medium">최근 실거래 (최저)</p>
                                            <p className="text-xl font-medium text-white/80">{formatPrice(sizeData.recent_lowest)}</p>
                                        </div>

                                        <div className="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-white/5">
                                            <p className="text-sm text-white/60 font-semibold">현재 최저호가</p>
                                            <p className="text-2xl font-extrabold text-white">{formatPrice(sizeData.current_ask)}</p>
                                        </div>
                                    </div>

                                    {/* MDD 뱃지 */}
                                    <div className="flex items-center justify-between mt-auto">
                                        <p className="text-xs text-white/30 font-medium">최고가 대비 하락률</p>
                                        <div className={`px-4 py-2 rounded-xl border flex items-center ${badgeColor}`}>
                                            <Activity size={18} className="mr-2" />
                                            <span className="font-black text-xl">
                                                {isDrop ? "" : "+"}{mdd.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>

                                </div>
                            </motion.div>
                        );
                    })}
                </div>

                {/* 최근 거래 내역 리스트 요약 (84㎡ 기준 하이라이트) */}
                <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
                    className="p-8 rounded-3xl bg-white/5 border border-white/10"
                >
                    <h3 className="text-xl font-bold mb-6 flex items-center">
                        <ArrowRight size={20} className="mr-2 text-indigo-400" /> 국민평형(84㎡) 최근 실거래 이력
                    </h3>
                    <div className="grid grid-cols-1 divide-y divide-white/5">
                        {data.sizes['84'].recent_deals.map((deal: any, i: number) => (
                            <div key={i} className="flex justify-between py-4 hover:bg-white/5 px-4 rounded-lg transition-colors">
                                <span className="text-white/60">{deal.date}</span>
                                <span className="font-bold">{formatPrice(deal.price)}</span>
                            </div>
                        ))}
                    </div>
                </motion.div>

            </div>
        </div>
    );
}
