'use client';
import {useState} from 'react';
import {supabase} from '@/utils/supabase';
import {siteInfo} from '@/lib/site-info';
export default function WithdrawAccount(){
 const [confirmation,setConfirmation]=useState(''),[busy,setBusy]=useState(false),[message,setMessage]=useState('');
 async function withdraw(){
  if(confirmation!=='탈퇴'||busy)return;
  setBusy(true);setMessage('');
  try{
   const {data:{session}}=await supabase.auth.getSession();
   if(!session)throw new Error('다시 로그인해 주세요.');
   const response=await fetch('/api/member/withdraw',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${session.access_token}`},body:JSON.stringify({confirmation})});
   const body=await response.json();if(!response.ok)throw new Error(body.error);
   await supabase.auth.signOut({scope:'local'});
   location.assign('/account/withdrawn');
  }catch(error){setMessage(error instanceof Error?error.message:'탈퇴 요청을 처리하지 못했습니다.');setBusy(false);}
 }
 return <details className="rt-panel member-withdraw"><summary>회원 탈퇴</summary><p>관심 단지, 저장한 리포트, 가격 알림, 프로필과 시장톡 의견이 함께 삭제되며 복구할 수 없습니다. 카카오 회원은 서비스 연결도 해제합니다.</p><p>요청이 접수되면 회원 기능을 즉시 제한하고 삭제를 처리합니다. 처리에 실패한 요청은 자동 재시도합니다.</p><label htmlFor="withdraw-confirm">계속하려면 ‘탈퇴’를 입력해 주세요.</label><input id="withdraw-confirm" autoComplete="off" value={confirmation} onChange={e=>setConfirmation(e.target.value)} disabled={busy}/><button className="rt-button" disabled={busy||confirmation!=='탈퇴'} onClick={()=>void withdraw()}>{busy?'접수 중…':'회원 탈퇴 요청'}</button><p role="status">{message}</p><a className="rt-link" href={`mailto:${siteInfo.contactEmail}`}>탈퇴 관련 문의</a></details>;
}
