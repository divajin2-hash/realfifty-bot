export function GET() {
    return Response.json(
        { error: '리포트 파일 다운로드는 제공하지 않습니다. 리포트 화면에서 분석 근거를 확인해 주세요.' },
        { status: 410, headers: { 'Cache-Control': 'no-store' } },
    );
}
