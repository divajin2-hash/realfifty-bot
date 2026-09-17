import type { Metadata } from 'next';
import { readUniverse, readComplex } from '@/lib/complex-data';
import ComplexTerminal from './ComplexTerminal';

export const dynamic = 'force-dynamic';
export const metadata: Metadata = { title: '단지 분석 | RealFifty', description: '대한민국 대표 50개 아파트의 평형별 실거래, 최저호가와 가격 괴리를 분석합니다.' };

export default async function ComplexPage({ searchParams }: { searchParams: Promise<{ id?: string; area?: string; tab?: string }> }) {
  const query = await searchParams;
  const { summaries, updatedAt } = await readUniverse();
  const requested = summaries.find(c => c.id === query.id);
  const initial = requested || summaries.find(c => c.name === '아시아선수촌') || summaries[0];
  const detail = initial ? await readComplex(initial.id) : null;
  return <ComplexTerminal key={`${initial?.id}:${query.area || ""}:${query.tab || ""}`} summaries={summaries} initialDetail={detail} updatedAt={updatedAt} initialArea={query.area} initialTab={query.tab} />;
}
