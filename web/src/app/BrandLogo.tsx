import Link from 'next/link';
import Image from 'next/image';
import './brand.css';
export default function BrandLogo(){return <Link href="/" className="rf-brand" aria-label="RealFifty 홈으로"><Image src="/realfifty-mark.svg" alt="" width={42} height={42} priority/><span className="rf-brand-word">Real<span>Fifty</span><small>주택시장 데이터 인사이트</small></span></Link>;}
