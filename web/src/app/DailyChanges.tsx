import Link from 'next/link';
import { readDailyChanges } from '@/lib/daily-changes';
import { price, percent } from '@/lib/complex-model';
import ChangePatterns from './ChangePatterns';
import { Metric } from './TerminalShell';
export default async function DailyChanges({stamp}:{stamp:string}) {
 const d=await readDailyChanges(stamp);
 return <section className="rt-panel"><div className="rf-eyebrow">DAILY / OBSERVED CHANGES</div><h2>오늘 포착한 변화</h2>
 {!d ? <p>비교 가능한 수집 자료를 확인하고 있습니다. 자료 부족을 변화 없음으로 표시하지 않습니다.</p> : <>
 <p>{d.previousDate} → {d.date} 수집분 비교 · 양쪽 모두 호가가 있는 {d.comparable}개 평형 기준</p>
 <div className="rt-grid three"><Metric label="↑ 최저호가 상승" value={`${d.rises}개 평형`} note="최저 매물 교체에 따른 변화 포함"/><Metric label="↓ 최저호가 하락" value={`${d.falls}개 평형`} note="실제 체결 가격의 하락과 구분"/><Metric label="변동 없음" value={`${d.unchanged}개 평형`} note="동일 타입의 수집 최저호가 비교"/></div>
 <p>새로 호가 확인 {d.appeared}개 · 호가가 사라진 평형 {d.disappeared}개 · 자료 누락·면적 변경으로 제외 {d.missing}개. 호가 유무의 전환은 가격 등락에 포함하지 않습니다.</p>
 <ChangePatterns data={d}/>
 <details><summary>변화한 {d.rows.length}개 평형 모두 보기</summary><div className="rt-table-wrap"><table className="rt-table"><thead><tr><th>단지·평형</th><th>이전 → 현재</th><th>변화율</th></tr></thead><tbody>{d.rows.map(r=><tr key={`${r.id}:${r.area}`}><td><Link href={`/complex?id=${encodeURIComponent(r.id)}&area=${encodeURIComponent(r.area)}`}>{r.name} ↗<br/><small>{r.label}</small></Link></td><td>{price(r.before)} → {price(r.after)}</td><td>{r.percent>0?'↑':'↓'} {percent(r.percent)}</td></tr>)}</tbody></table></div></details>
 </>}
 <p className="rt-caption">최저호가 변화는 동일 매물의 가격 수정과 다릅니다. 저가 매물의 등록·철회로도 바뀔 수 있습니다. 새로 확인된 실거래 건수는 거래 이력의 수집 전후 대조가 확보될 때 제공합니다. 최근 실거래 가격이 바뀐 평형 수를 신규 거래 건수로 세지 않습니다.</p>
 </section>;
}
