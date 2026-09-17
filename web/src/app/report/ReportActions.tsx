'use client';
import {SaveReport} from '../MemberActions';
export default function ReportActions({ date }: {
    date: string;
}) { return <div className="rt-actions"><SaveReport date={date}/><button className="rt-button" onClick={() => window.print()}>인쇄 / PDF 저장</button></div>; }
