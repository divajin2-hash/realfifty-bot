import TerminalShell from '../../TerminalShell';import FeedbackDesk from './FeedbackDesk';
export default function Page(){return <TerminalShell active="/admin/feedback" eyebrow="OPERATOR" title="의견 접수함" description="비공개 접수 내용을 검토하고 처리 상태를 관리합니다."><FeedbackDesk/></TerminalShell>;}
