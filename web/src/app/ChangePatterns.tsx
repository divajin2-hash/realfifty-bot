import Link from 'next/link';
import type { DailyChanges } from '@/lib/daily-changes';
export default function ChangePatterns({data:d}:{data:DailyChanges}) {
 const grouped=new Map<string,{id:string;name:string;up:number;down:number}>();
 for(const row of d.rows){const g=grouped.get(row.id)||{id:row.id,name:row.name,up:0,down:0};if(row.after>row.before)g.up++;else if(row.after<row.before)g.down++;grouped.set(row.id,g);}
 const groups=[...grouped.values()].sort((a,b)=>(b.up+b.down)-(a.up+a.down)||a.name.localeCompare(b.name,'ko'));
 const mixed=groups.filter(g=>g.up>0&&g.down>0);
 const down=groups.filter(g=>g.down>=2&&g.up===0);
 const up=groups.filter(g=>g.up>=2&&g.down===0);
 const list=(items:typeof groups)=><ul>{items.slice(0,3).map(g=><li key={g.id}><Link href={`/complex?id=${encodeURIComponent(g.id)}`}>{g.name} ↗</Link> · 상승 {g.up}개 / 하락 {g.down}개</li>)}</ul>;
 return <div className="daily-patterns"><h3>오늘 변화의 특징</h3>
 <p><strong>{d.comparable ? `비교 가능한 평형의 ${(100*d.rows.length/d.comparable).toFixed(1)}%에서 최저호가가 바뀌었습니다.`:'비교 가능한 평형이 없습니다.'}</strong> {d.falls>d.rises?'하락한 평형이 상승한 평형보다 많지만':d.rises>d.falls?'상승한 평형이 하락한 평형보다 많지만':'상승·하락한 평형 수가 같으며'}, 변동 없는 평형은 {d.unchanged}개입니다. 평형 수 기준의 분포이며 거래량이나 단지 규모로 가중한 시장 지수는 아닙니다.</p>
 <div className="rt-grid three">
 <article className="rt-panel"><h3>↕ 같은 단지, 다른 방향</h3>{mixed.length?<><p>{mixed.length}개 단지에서 상승과 하락이 함께 관측됐습니다. 단지 전체가 한 방향으로 움직였다고 보기 어렵습니다.</p>{list(mixed)}<p>특정 평형만 상승했다면 저가 매물의 소멸이나 평형별 매물 구성 차이부터 확인할 필요가 있습니다.</p></>:<p>이번 비교에서 상승·하락이 동시에 나타난 단지는 없습니다.</p>}</article>
 <article className="rt-panel"><h3>↓ 여러 평형에서 동반 하락</h3>{down.length?<><p>{down.length}개 단지에서 두 개 이상 평형이 하락했고, 상승한 평형은 없었습니다.</p>{list(down)}<p>더 낮은 최저 매도호가가 여러 타입에서 관측됐습니다. 이후 수집과 후속 실거래에서도 이어지는지 확인하세요.</p></>:<p>두 개 이상 평형이 하락하고 상승 평형이 없는 단지는 이번 비교에 없습니다.</p>}</article>
 <article className="rt-panel"><h3>↑ 여러 평형에서 동반 상승</h3>{up.length?<><p>{up.length}개 단지에서 두 개 이상 평형이 상승했고, 하락한 평형은 없었습니다.</p>{list(up)}<p>저가 매물이 빠져도 최저호가는 올라갑니다. 실제 체결 증가나 매도자의 가격 인상으로 단정할 수 없습니다.</p></>:<p>두 개 이상 평형이 상승하고 하락 평형이 없는 단지는 이번 비교에 없습니다.</p>}</article>
 </div><p className="rt-caption">변화가 확인된 평형을 단지별로 묶은 관측입니다. 변동 없는 평형과 호가 누락은 ‘전체 평형 동반 상승·하락’의 근거가 아닙니다. 예시는 변화한 평형 수가 많은 순으로 최대 세 단지입니다. 한 번의 수집 간 비교이며 연속 추세나 집주인의 심리를 뜻하지 않습니다.</p>
 </div>;
}
