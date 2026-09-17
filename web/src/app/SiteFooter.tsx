import { siteInfo } from '@/lib/site-info';
import Link from 'next/link';
import FeedbackButton from './FeedbackButton';

export default function SiteFooter() {
    return <footer className="rf-footer">
        <span>RealFifty · 운영 {siteInfo.operator}<b>국토교통부 실거래 · 매물 최저호가</b></span>
        <div className="footer-mobile-feedback"><FeedbackButton/></div>
        <span>50개 선정 단지 표본 · 전국 시장 전체를 대표하지 않습니다<br />
            <a href={`mailto:${siteInfo.contactEmail}`} style={{ display: 'inline-block', padding: '12px 0', overflowWrap: 'anywhere' }}>문의 · {siteInfo.contactEmail}</a>
            <nav aria-label="이용 안내"><Link href="/guide">이용 가이드</Link>{' · '}<Link href="/improvements">개선 소식</Link>{' · '}<Link href="/privacy">개인정보처리방침</Link>{' · '}<Link href="/terms">이용약관</Link></nav>
        </span>
    </footer>;
}
