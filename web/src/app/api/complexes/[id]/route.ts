import { readComplex } from '@/lib/complex-data';
export const dynamic = 'force-dynamic';
export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const detail = await readComplex((await params).id);
    return detail ? Response.json(detail, { headers: { 'Cache-Control': 'no-store' } })
      : Response.json({ error: '단지를 찾을 수 없습니다.' }, { status: 404 });
  } catch {
    return Response.json({ error: '로컬 데이터를 읽지 못했습니다.' }, { status: 503 });
  }
}
