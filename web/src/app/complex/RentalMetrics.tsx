import {positive, price, type AreaStat} from '@/lib/complex-model';
export default function RentalMetrics({stat}:{stat:AreaStat}){
 const sale=stat.current_lowest_ask, rent=stat.jeonse_lowest_ask;
 const noRentListings=stat.jeonse_count===0;
 const valid=!noRentListings&&positive(sale)&&positive(rent);
 const count=(v:number|undefined)=>typeof v==='number'&&Number.isFinite(v)&&v>=0?`${v.toLocaleString('ko-KR')}건`:'확인 필요';
 return <section className="rf-panel" aria-label="선택 평형 매매·전세"><h3>선택 평형의 매매·전세</h3><div className="rf-metrics">
 <div className="rf-metric"><span>매매 매물</span><strong>{count(stat.sale_count)}</strong><small>수집 API의 등록 건수</small></div>
 <div className="rf-metric"><span>전세 매물</span><strong>{count(stat.jeonse_count)}</strong><small>수집 API의 등록 건수</small></div>
 <div className="rf-metric"><span>최저 전세호가</span><strong>{noRentListings?'매물 없음':price(rent)}</strong><small>현재 선택한 타입</small></div>
 <div className="rf-metric"><span>호가 기준 전세가율</span><strong>{valid?`${(rent/sale*100).toFixed(1)}%`:'—'}</strong><small>최저 전세호가 ÷ 최저 매매호가</small></div>
 </div><p>매매·전세 호가 차이 <strong>{valid?`${((sale-rent)/100000000).toLocaleString('ko-KR',{maximumFractionDigits:2})}억`:'—'}</strong>{valid?` · 매매호가의 ${((sale-rent)/sale*100).toFixed(1)}%`:''}</p><p className="rf-muted">서로 다른 매물의 최저가격을 비교한 참고값입니다. 실제 투자금이 아니며 세금·수수료·대출·보증금 반환 부담은 포함하지 않습니다. 등록 건수에는 중복이 있을 수 있습니다. 전세 매물이 없으면 전세호가·전세가율·호가 차이를 제공하지 않습니다.</p></section>;
}
