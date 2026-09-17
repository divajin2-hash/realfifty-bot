import { readUniverse } from '@/lib/complex-data';
import { compareVolume } from '@/lib/market-reading';
import type { MarketData } from '@/lib/market-data';
import { percent } from '@/lib/complex-model';
export default async function MarketInterpretation({data:d}:{data:MarketData}) {
 const u=await readUniverse();
 const volume=Date.parse(d.updatedAt)===Date.parse(u.updatedAt)?compareVolume(u.groups):null;
 return <section className="rt-panel"><div className="rf-eyebrow">OBSERVATION / INTERPRETATION / NEXT</div><h2>이 숫자를 어떻게 읽을까요?</h2>
 <h3>관측 · 가격과 호가의 간격</h3><p>최근 거래가 있는 {d.comparable.length}개 대표 타입 중 {d.below}개에서 최저호가가 최근 실거래보다 낮습니다. 평균 간격은 {percent(d.meanGap)}입니다.</p>
 <h3>해석 · 매물과 체결 조건을 함께 확인</h3><p>현재 매도 호가와 과거 체결 가격의 차이입니다. 층·향·상태와 거래 시점이 달라, 이 간격만으로 시장 하락이나 매수 기회라고 판단할 수 없습니다.</p>
 {volume && <><h3>거래량 · 같은 날짜 구간의 잠정 비교</h3><p>{volume.previousStart}~{volume.previousEnd}: {volume.previous}건 → {volume.start}~{volume.end}: {volume.current}건. 현재 자료의 차이는 {volume.change===null?'비교 불가':percent(volume.change)}입니다.</p><p>같은 거래는 여러 타입에 연결돼도 한 번만 집계합니다. 최근 계약은 신고가 덜 반영돼 있으므로, 기간을 맞췄어도 최종 증감률은 아닙니다.</p></>}
 <h3>다음 확인 · 후속 거래와 매물 변화</h3><p>같은 면적의 후속 체결에서도 가격 차이가 이어지는지 확인하세요. 최저호가 변화와 매물수 증감이 함께 나타나는지도 살펴보되, 매물 감소를 거래 성사로 간주하지 않습니다. 선정 단지의 관측을 전국 시장으로 확대 해석하지 않습니다.</p>
 </section>;
}
