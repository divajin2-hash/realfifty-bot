import Link from 'next/link';
import TerminalShell, { Metric } from '../TerminalShell';
import { readUniverse } from '@/lib/complex-data';
import { compareVolume } from '@/lib/market-reading';

export const dynamic = 'force-dynamic';
export default async function News() {
  const universe = await readUniverse().catch(() => null);
  const data = universe ? compareVolume(universe.groups) : null;
  const count = (n: number) => <>{n.toLocaleString('ko-KR')}<small style={{ fontFamily: 'inherit', fontSize: '0.65em' }}> 건</small></>;
  return <TerminalShell active="/news" eyebrow="MARKET / READING DATA" title="데이터로 읽는 시장"
    description="같은 기준으로 비교하고, 숫자가 말하지 않는 부분까지 확인합니다.">
    <section className="rt-hero"><span className="rf-badge amber">첫 번째 질문 · 거래량</span>
      <h2>거래가 정말 줄었을까요?</h2>
      <p>한 달 전체와 이번 달 일부를 비교하면 감소폭이 과장될 수 있습니다. 두 달의 같은 날짜 구간을 나란히 살펴봅니다.</p>
      <p className="rt-note">분석 범위: RealFifty 선정 단지의 평형에 연결된 거래입니다. 서울·경기도·전국 전체 거래량을 나타내지 않습니다.</p>
    </section>
    {!data ? <section className="rt-panel"><h2>비교 자료를 확인하고 있습니다</h2><p>최신 집계 시점과 거래 식별 정보를 확인할 수 있어야 비교를 제공합니다. 매월 첫날에는 전일까지의 이번 달 비교 구간이 없어 기다립니다. 자료 부족을 거래 0건으로 표시하지 않습니다.</p></section> : <>
      <section className="rt-panel"><div className="rf-eyebrow">01 / SAME PERIOD</div><h2>먼저, 비교 기간을 맞췄습니다</h2>
        <p>{data.complexes}개 선정 단지 · 계약일 기준 · 자료 생성 {new Date(data.stamp).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })} KST</p>
        <div className="rt-grid three">
          <Metric label="지난달 같은 구간" value={count(data.previous)} note={`${data.previousStart} ~ ${data.previousEnd}`} />
          <Metric label="이번 달 같은 구간" value={count(data.current)} note={`${data.start} ~ ${data.end}`} />
          <Metric label="현재 자료에서 관찰된 차이" value={data.change === null ? '비교 불가' : `${data.change > 0 ? '+' : ''}${data.change.toFixed(1)}%`} note="지난달 같은 구간 대비 · 최종 증감률 아님" />
        </div>
        <p>당일 계약은 제외하고, 두 달에 모두 존재하는 날짜까지만 비교합니다. 같은 거래가 여러 평형에 연결돼도 한 번만 셉니다.</p>
      </section>
      <section className="rt-panel"><div className="rf-eyebrow">02 / PROVISIONAL</div><h2>기간을 맞춰도 신고 진행 상태는 다릅니다</h2>
        <span className="rf-badge amber">잠정 집계 · 확정 판단 유보</span>
        <p>{data.change === null ? '지난달 비교 건수가 없어 증감률을 계산하지 않습니다.' : `현재 조회된 자료에서는 이번 달 거래가 지난달 같은 구간보다 ${data.change < 0 ? '적게' : data.change > 0 ? '많이' : '같게'} 확인됩니다.`} 최근 계약은 아직 신고가 추가될 수 있습니다.</p>
        <p>지난달 거래는 신고가 반영될 시간이 더 길었습니다. 두 시점의 신고 진행 정도까지 같게 맞춘 비교는 아니며, 현재 차이를 최종 감소율이나 증가율로 읽으면 안 됩니다.</p>
      </section>
    </>}
    <section className="rt-panel"><div className="rf-eyebrow">03 / LIMITS</div><h2>이 숫자만으로 알 수 없는 것</h2>
      <ul><li>거래량의 변화만으로 집값의 상승·하락을 판단할 수 없습니다.</li><li>매수 심리나 대출 규제가 변화의 원인인지 입증하지 않습니다.</li><li>선정 단지의 변화를 다른 지역이나 주택시장 전체로 일반화할 수 없습니다.</li></ul>
      <Link className="rt-download" href="/complex">관심 단지의 실제 거래 살펴보기 →</Link>
    </section>
    <details className="rt-panel rt-method"><summary>집계 기준과 자동 갱신 안내</summary>
      <p>서비스 데이터가 갱신되면 같은 계산 기준을 적용합니다. 이 페이지를 열 때 유료 AI를 호출하지 않습니다.</p>
      <p>현재 매칭 데이터의 일반 매매와 분양권·입주권 거래를 포함하며 해제·직거래는 제외합니다. 평형에 연결되지 않은 거래는 포함하지 않아, 선정 단지의 전체 계약 건수와도 다를 수 있습니다.</p>
      <p>데이터 생성 후 3일이 지났거나 집계 시점이 불일치하거나 거래 식별자가 누락되면 비교를 숨깁니다. 신고 추가·해제·매칭 정정으로 과거 수치도 바뀔 수 있습니다.</p>
    </details>
  </TerminalShell>;
}
