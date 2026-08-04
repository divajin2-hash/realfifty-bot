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

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { reportDate, nickname, content } = body;

        if (!reportDate || !nickname || !content) {
            return NextResponse.json({ error: 'Missing fields' }, { status: 400 });
        }

        const { data, error } = await supabase
            .from('report_comments')
            .insert([
                {
                    report_date: reportDate,
                    user_name: nickname,
                    content: content
                }
            ]);

        if (error) throw error;
        return NextResponse.json({ success: true });
    } catch (e) {
        console.error(e);
        return NextResponse.json({ error: 'Failed to post' }, { status: 500 });
    }
}
