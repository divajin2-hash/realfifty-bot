export const districts: Record<string, string> = { '11110': '서울 종로구', '11140': '서울 중구', '11170': '서울 용산구', '11200': '서울 성동구', '11215': '서울 광진구', '11230': '서울 동대문구', '11260': '서울 중랑구', '11290': '서울 성북구', '11305': '서울 강북구', '11320': '서울 도봉구', '11350': '서울 노원구', '11380': '서울 은평구', '11410': '서울 서대문구', '11440': '서울 마포구', '11470': '서울 양천구', '11500': '서울 강서구', '11530': '서울 구로구', '11545': '서울 금천구', '11560': '서울 영등포구', '11590': '서울 동작구', '11620': '서울 관악구', '11650': '서울 서초구', '11680': '서울 강남구', '11710': '서울 송파구', '11740': '서울 강동구', '41135': '경기 성남시 분당구', '41290': '경기 과천시', '41210': '경기 광명시', '41450': '경기 하남시' };
export interface Article {
    id: string;
    title: string;
    link: string;
    source: string;
    pub_date: string;
}
export interface Scope {
    lawd_code: string;
    district: string;
    dong: string;
    start: string;
    end: string;
    baseline_start: string;
    baseline_end: string;
    claim: string;
    metric: 'price_direction' | 'volume_change';
    direction: 'up' | 'down';
    scope_confirmed: boolean;
}
export interface AuditJob {
    id: string;
    article: Article;
    scope: Scope;
    status: string;
    created_at: string;
}
export interface AuditResult {
    schema_version: number;
    job_id: string;
    article: Article;
    scope: Scope;
    status: string;
    verdict: string;
    reason: string;
    collected_at: string;
    provisional: boolean;
    stats: {
        current_count: number;
        baseline_count: number;
        volume_change: number | null;
        up: number;
        down: number;
        flat: number;
        unmatched: number;
        comparable: number;
        price_candidates: number;
        coverage: number;
        cancelled: number;
        direct: number;
        unknown_type: number;
        invalid: number;
    };
    method: string[];
    sources: {
        lawd_code: string;
        month: string;
        total: number;
        pages: number;
    }[];
    rows: {
        date: string;
        name: string;
        dong: string;
        area: number;
        floor: number;
        price: number;
        baseline_median: number | null;
        change: number | null;
        direction: string;
    }[];
    commentary?: {
        summary: string;
        limitations: string[];
    };
    error?: string;
}
export function validateScope(input: unknown): Scope {
    if (!input || typeof input !== 'object')
        throw new Error('검증 범위를 입력하세요.');
    const s = input as Record<string, unknown>;
    const str = (key: string) => typeof s[key] === 'string' ? (s[key] as string).trim() : '';
    const lawd = str('lawd_code');
    if (!districts[lawd])
        throw new Error('지원하는 시군구를 선택하세요.');
    const dates = ['start', 'end', 'baseline_start', 'baseline_end'].map(key => str(key));
    if (dates.some(v => !/^\d{4}-\d{2}-\d{2}$/.test(v) || !Number.isFinite(Date.parse(v)) || new Date(v).toISOString().slice(0, 10) !== v))
        throw new Error('올바른 날짜가 필요합니다.');
    const [start, end, baseline_start, baseline_end] = dates;
    const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
    if (start > end || baseline_start > baseline_end || baseline_end >= start || end > today)
        throw new Error('비교 기간은 대상 기간보다 앞서야 하며 미래일을 포함할 수 없습니다.');
    if ((Date.parse(end) - Date.parse(baseline_start)) / 86400000 > 730)
        throw new Error('한 번의 검증 범위는 비교 기간 포함 2년 이내입니다.');
    const claim = str('claim');
    const dong = str('dong');
    if (claim.length < 8 || claim.length > 1500 || dong.length > 40)
        throw new Error('기사의 검증할 주장을 8~1500자로 입력하세요.');
    if (!['price_direction', 'volume_change'].includes(str('metric')) || !['up', 'down'].includes(str('direction')))
        throw new Error('검증 지표와 방향을 선택하세요.');
    if (s.scope_confirmed !== true)
        throw new Error('기사의 지역·기간과 검증 범위 일치를 확인하세요.');
    if (s.metric === 'volume_change') {
        const fullMonth = (a: string, b: string) => a.slice(8) === '01' && new Date(Date.parse(b) + 86400000).getUTCDate() === 1;
        const months = (a: string, b: string) => (Number(b.slice(0, 4)) - Number(a.slice(0, 4))) * 12 + Number(b.slice(5, 7)) - Number(a.slice(5, 7));
        const sameDays = Date.parse(end) - Date.parse(start) === Date.parse(baseline_end) - Date.parse(baseline_start);
        if (!sameDays && !(fullMonth(start, end) && fullMonth(baseline_start, baseline_end) && months(start, end) === months(baseline_start, baseline_end)))
            throw new Error('거래량 비교는 같은 일수 또는 같은 개수의 완료 월로 설정하세요.');
    }
    return { lawd_code: lawd, district: districts[lawd], dong, start, end, baseline_start, baseline_end, claim, metric: s.metric as Scope['metric'], direction: s.direction as Scope['direction'], scope_confirmed: true };
}
export function articleTriage(title: string) {
    const broad = /전국|지방|수도권/.test(title);
    const volume = /거래량|거래.*건|거래.*증가|거래.*감소|거래절벽|거래 절벽/.test(title);
    const index = /아파트값|아파트 값|매맷값|매매가격|매매 가격|주택.*가격|주째/.test(title);
    if (index)
        return { label: '가격지수 원자료 필요', note: '가격지수는 조사 표본과 산식을 확인해야 합니다. 지역 실거래 분포는 보조 분석으로만 사용합니다.', priority: 2 };
    if (broad)
        return { label: '광역 통계 범위 확인', note: '전국·지방 등 광역 주장은 전체 지역의 동일 기간 통계가 필요합니다. 특정 구나 선정 단지로 대체하지 않습니다.', priority: 3 };
    if (volume)
        return { label: '거래량 검증 후보', note: '기사 본문에서 지역·주택 유형·계약기간·비교기간을 확인하면 실거래 건수와 대조할 수 있습니다.', priority: 0 };
    if (/신고가|급락|상승거래|하락거래/.test(title))
        return { label: '개별 거래 확인 후보', note: '해당 단지·타입·거래일을 확인하세요. 신고가 여부는 충분한 과거 이력이 필요하며 현재의 기간 비교와 구분합니다.', priority: 1 };
    return { label: '검증 지표 확인 필요', note: '전망·심리·경매·토지 등은 아파트 매매 실거래 API만으로 검증할 수 없습니다.', priority: 4 };
}
