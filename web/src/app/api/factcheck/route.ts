import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { auditRoot, readArticles, readAudits } from '@/lib/factcheck-data';
import { validateScope } from '@/lib/factcheck-model';
import {adminAccess} from '@/lib/admin-access';
export const dynamic = 'force-dynamic';
export async function POST(request: Request) {
    if(!await adminAccess(request))return Response.json({error:"운영자 권한이 필요합니다."},{status:403});
    if(process.env.VERCEL==='1')return Response.json({error:'검증 요청은 로컬 검증기에서 등록해 주세요.'},{status:503});
    const origin = request.headers.get('origin');
    if (origin && origin !== new URL(request.url).origin)
        return Response.json({ error: '다른 출처의 요청은 허용하지 않습니다.' }, { status: 403 });
    if (Number(request.headers.get('content-length') || 0) > 20000)
        return Response.json({ error: '요청이 너무 큽니다.' }, { status: 413 });
    try {
        const body = await request.text();
        if (body.length > 20000)
            return Response.json({ error: '요청이 너무 큽니다.' }, { status: 413 });
        const payload = JSON.parse(body);
        const scope = validateScope(payload.scope);
        const article = (await readArticles()).find(a => a.id === payload.article_id);
        if (!article)
            return Response.json({ error: '기사 목록을 새로고침하세요.' }, { status: 404 });
        const id = createHash('sha256').update(JSON.stringify({ article_id: article.id, scope })).digest('hex').slice(0, 32);
        const dir = path.join(auditRoot(), 'queue');
        await fs.mkdir(dir, { recursive: true });
        try {
            await fs.writeFile(path.join(dir, `${id}.json`), JSON.stringify({ id, article, scope, status: 'queued', created_at: new Date().toISOString() }, null, 2), { encoding: 'utf8', flag: 'wx' });
        }
        catch (e) {
            if ((e as NodeJS.ErrnoException).code !== 'EEXIST')
                throw e;
        }
        return Response.json({ id, status: 'queued', message: '검증 범위를 저장했습니다. 지역 실거래 수집 작업이 완료되면 결과가 표시됩니다.' });
    }
    catch (e) {
        if (e instanceof SyntaxError)
            return Response.json({ error: '요청 형식 오류' }, { status: 400 });
        if (e instanceof Error && !('code' in e))
            return Response.json({ error: e.message }, { status: 400 });
        return Response.json({ error: '검증 요청을 저장하지 못했습니다.' }, { status: 500 });
    }
}
export async function GET(request: Request) { if(!await adminAccess(request))return Response.json({error:"운영자 권한이 필요합니다."},{status:403}); const id = new URL(request.url).searchParams.get('id'); const audits = await readAudits(); if (!id)
    return Response.json(audits, { headers: { 'Cache-Control': 'no-store' } }); const result = audits.results.find(r => r.job_id === id); if (!result)
    return Response.json({ error: '아직 수집된 근거가 없습니다.' }, { status: 404 }); let sourceRows = null; try {
    sourceRows = JSON.parse(await fs.readFile(path.join(auditRoot(), 'raw', `${result.job_id}.json`), 'utf8'));
}
catch { } return Response.json({ ...result, raw_source_rows: sourceRows }, { headers: { 'Content-Disposition': `attachment; filename="realfifty-audit-${id}.json"`, 'Cache-Control': 'no-store' } }); }
