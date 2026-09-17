import SampleScope from './SampleScope';
import SiteFooter from './SiteFooter';
import type { ReactNode } from 'react';
import Sidebar from './Sidebar';
import './complex/terminal.css';
import './terminal-pages.css';
export default function TerminalShell({ active, eyebrow, title, description, updatedAt, children }: {
    active: string;
    eyebrow: string;
    title: string;
    description: string;
    updatedAt?: string;
    children: ReactNode;
}) {
    return <div className={`app-wrapper rf-app${active === "/report" ? " rf-report-page" : ""}`}><Sidebar activePath={active}/><main className="rf-workspace">
  <div className="rf-topbar"><div><span className="rf-kicker">REALFIFTY / HOUSING INTELLIGENCE</span></div><div className="rf-source"><span className="rf-status-dot"/><span>{updatedAt ? `데이터 파일 갱신 ${new Date(updatedAt).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul', hour12: false })} KST` : '근거와 해석을 구분하는 주택시장 분석'}</span></div></div>
  <header className="rf-page-heading"><div><div className="rf-eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div><span className="rf-badge mint">REALFIFTY RESEARCH</span></header>
  {children}<SampleScope/><SiteFooter/>
 </main></div>;
}
export function Metric({ label, value, note }: {
    label: string;
    value: ReactNode;
    note: string;
}) { return <article className="rt-metric"><span>{label}</span><strong className="rf-number">{value}</strong><p>{note}</p></article>; }
export function Methodology() { return <details className="rt-panel rt-method"><summary>지표 산식과 표본 기준</summary><p>단지별 대표 타입은 유효한 호가·실거래가 있는 타입을 우선하고, 1년 이내 거래와 전용 84㎡ 근접도를 순서대로 적용합니다. 평균은 거래가 365일 이내인 비교 가능 단지의 단순 평균이며 결측값은 제외합니다.</p><p>호가 괴리 = (현재 최저호가 ÷ 최근 실거래가 − 1) × 100. 고점 대비 = (가격 ÷ 해당 타입 관측 최고 실거래가 − 1) × 100. 최근 거래와 현재 매물의 층·향·상태가 달라질 수 있습니다. 월 거래량은 타입 고점과 연결되고 고점 대비 가격 비율이 20~200%인 유효 거래 집계입니다. 회복률은 해당 비율의 월 중앙값이며 5건 미만인 월은 제공되지 않습니다. 따라서 전체 계약 건수와 다를 수 있습니다. 진행 중인 월은 신고 지연과 미완결 기간의 영향을 받습니다.</p></details>; }
