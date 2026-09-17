import Link from 'next/link';
import TerminalShell from '../../TerminalShell';
import {siteInfo} from '@/lib/site-info';
export default function Page(){return <TerminalShell active="/account" eyebrow="MY REALFIFTY" title="탈퇴 요청을 접수했습니다" description="로그아웃되었습니다. 계정과 회원 데이터 삭제를 처리합니다."><section className="rt-panel"><p>처리는 보통 곧 완료되며, 연결 서비스 오류가 발생하면 자동으로 다시 시도합니다. 삭제가 완료되면 이전 기록은 복구할 수 없습니다.</p><p>처리 중에는 재가입을 잠시 기다려 주세요. 다음 날까지 문제가 남으면 <a href={`mailto:${siteInfo.contactEmail}`}>{siteInfo.contactEmail}</a>로 문의해 주세요.</p><Link className="rt-button" href="/">시장 화면으로 돌아가기</Link></section></TerminalShell>;}
