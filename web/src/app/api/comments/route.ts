import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const date = searchParams.get('date');

    if (!date) return NextResponse.json({ comments: [] });

    const { data, error } = await supabase
        .from('report_comments')
        .select('*')
        .eq('report_date', date)
        .order('created_at', { ascending: false });

    if (error) {
        console.error(error);
        return NextResponse.json({ comments: [] });
    }

    return NextResponse.json({ comments: data });
}

export async function POST() {
    return NextResponse.json({ error: '이전 리포트 댓글 작성은 종료되었습니다. 로그인 후 단지 시장톡을 이용해 주세요.' }, { status: 410 });
}
