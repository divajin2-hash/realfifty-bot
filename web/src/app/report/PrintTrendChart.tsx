import type { MacroPoint } from '@/lib/market-data';

// Fixed viewBox keeps the printed chart independent of ResizeObserver timing.
export default function PrintTrendChart({data}: {data: MacroPoint[]}) {
 const rows=data.filter(d=>Number.isFinite(d.sample_count));
 if (!rows.length) return <p className="report-print-chart">시계열 데이터 없음</p>;
 const rates=rows.map(d=>d.recovery_rate).filter(Number.isFinite);
 const low=Math.floor(Math.min(...rates,100)/10)*10;
 const high=Math.max(low+10,Math.ceil(Math.max(...rates,100)/10)*10);
 const maxCount=Math.max(1,...rows.map(d=>d.sample_count));
 const x=(i:number)=>48+(i+.5)*620/rows.length;
 const y=(v:number)=>210-(v-low)/(high-low)*170;
 const path=rows.map((d,i)=>Number.isFinite(d.recovery_rate)?`${i===0||!Number.isFinite(rows[i-1].recovery_rate)?'M':'L'}${x(i)},${y(d.recovery_rate)}`:'').join(' ');
 return <svg className="report-print-chart" viewBox="0 0 730 260" role="img" aria-label="월별 실거래 회복률과 신고 거래 수">
 <text x="48" y="16" fontSize="11" fill="#254f80">선: 실거래 회복률 (%)</text><text x="450" y="16" fontSize="11" fill="#35574f">막대: 신고 거래 수 (건)</text>
 {[0,1,2,3,4].map(i=><g key={i}><line x1="48" x2="668" y1={40+i*42.5} y2={40+i*42.5} stroke="#d4dce2"/><text x="42" y={44+i*42.5} textAnchor="end" fontSize="10" fill="#374151">{(high-i*(high-low)/4).toFixed(0)}%</text><text x="677" y={44+i*42.5} fontSize="10" fill="#374151">{Math.round(maxCount*(1-i/4))}</text></g>)}
 {rows.map((d,i)=><g key={d.month}><rect x={x(i)-620/rows.length*.35} y={210-d.sample_count/maxCount*170} width={620/rows.length*.7} height={d.sample_count/maxCount*170} fill="#587e72"/>{(i%Math.ceil(rows.length/8)===0||i===rows.length-1)&&<text x={x(i)} y="229" textAnchor="middle" fontSize="10" fill="#374151">{d.month.slice(2)}</text>}</g>)}
 <path d={path} fill="none" stroke="#254f80" strokeWidth="2"/>
 </svg>;
}
