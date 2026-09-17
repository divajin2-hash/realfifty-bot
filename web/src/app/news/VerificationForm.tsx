'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {supabase} from '@/utils/supabase';
import { districts } from '@/lib/factcheck-model';
export default function VerificationForm({ articleId, title }: {
    articleId: string;
    title: string;
}) { const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false); const router = useRouter(); return <form onSubmit={async (e) => { e.preventDefault(); setBusy(true); setMessage('검증 범위를 저장하는 중입니다.'); const fields = new FormData(e.currentTarget); const scope = Object.fromEntries(fields); try {
    const {data:{session}}=await supabase.auth.getSession();
    const response = await fetch('/api/factcheck', { method: 'POST', headers: { 'Content-Type': 'application/json', ...(session?{Authorization:`Bearer ${session.access_token}`}:{}) }, body: JSON.stringify({ article_id: articleId, scope: { ...scope, scope_confirmed: fields.get('scope_confirmed') === 'on' } }) });
    const data = await response.json();
    setMessage(response.ok ? data.message : data.error);
    if (response.ok)
        router.refresh();
}
catch {
    setMessage('연결에 실패했습니다. 다시 시도하세요.');
}
finally {
    setBusy(false);
} }}><div className="rt-evidence"><div><label className="rt-small" htmlFor="claim">검증할 주장 · 원문에서 지역·기간이 드러나는 문장을 확인하세요</label><textarea id="claim" name="claim" required minLength={8} maxLength={1500} defaultValue={title} style={{ width: '100%', minHeight: 100, marginTop: 10, padding: 12, background: '#111d27', color: '#dce8ef', border: '1px solid #415361', borderRadius: 6, font: 'inherit', fontSize: 12 }}/><div className="rt-controls" style={{ marginTop: 12 }}><label className="rt-small" htmlFor="lawd">검증 지역</label><select name="lawd_code" id="lawd" required defaultValue=""><option value="" disabled>시군구 선택</option>{Object.entries(districts).map(([code, name]) => <option key={code} value={code}>{name}</option>)}</select><input name="dong" aria-label="법정동" placeholder="법정동 예: 잠실동 (빈칸은 구 전체)" maxLength={40}/></div><div className="rt-controls"><select name="metric" aria-label="검증 지표"><option value="price_direction">상승·하락 거래 분포</option><option value="volume_change">거래량 증감</option></select><select name="direction" aria-label="기사에서 주장하는 방향"><option value="up">기사 주장: 상승 / 증가</option><option value="down">기사 주장: 하락 / 감소</option></select></div></div><div><h3>기간을 같은 기준으로 맞추세요</h3><label className="rt-small">기사 대상 기간</label><div className="rt-controls"><input type="date" name="start" aria-label="대상 시작일" required/><span>~</span><input type="date" name="end" aria-label="대상 종료일" required/></div><label className="rt-small">비교 기준 기간</label><div className="rt-controls"><input type="date" name="baseline_start" aria-label="비교 시작일" required/><span>~</span><input type="date" name="baseline_end" aria-label="비교 종료일" required/></div><p>가격은 동일 단지·전용면적·층 구간의 비교 기간 중위가격과 대조합니다. 거래량은 같은 일수 또는 같은 수의 완료 월을 비교합니다.</p></div></div><label style={{ display: 'flex', gap: 10, alignItems: 'flex-start', margin: '18px 0', fontSize: 12, color: '#bdcbd5' }}><input type="checkbox" name="scope_confirmed" required/>원문을 확인했으며, 선택한 지역·기간이 검증할 주장과 일치합니다. 전국·지방 전체 주장에 특정 구의 결과를 일반화하지 않습니다.</label><div className="rt-actions"><button type="submit" className="rt-button" disabled={busy}>{busy ? '저장 중…' : '검증 요청 저장'}</button><span className="rt-small">자동 판정 전 지역 실거래 수집이 필요합니다.</span></div><p role="status" style={{ marginTop: 14 }}>{message}</p></form>; }
