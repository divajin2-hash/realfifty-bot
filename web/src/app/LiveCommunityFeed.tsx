"use client"
import React, { useEffect, useState } from 'react';
import { supabase } from '../utils/supabase';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

interface Comment {
    id: string;
    complex_name: string;
    persona_type: string;
    vote: 'bull' | 'bear' | 'neutral';
    content: string;
    created_at: string;
}

export default function LiveCommunityFeed() {
    const [comments, setComments] = useState<Comment[]>([]);

    useEffect(() => {
        const fetchComments = async () => {
            const { data, error } = await supabase
                .from('community_comments')
                .select('id, vote, content, created_at, persona_type, complexes(name)')
                .order('created_at', { ascending: false })
                .limit(4);

            if (data && !error) {
                const formatted = data.map((d: any) => ({
                    id: d.id,
                    complex_name: d.complexes?.name || '알수없음',
                    persona_type: d.persona_type,
                    vote: d.vote,
                    content: d.content,
                    created_at: d.created_at
                }));
                setComments(formatted);
            }
        };

        fetchComments();
        const interval = setInterval(fetchComments, 1000 * 60); // refresh every minute
        return () => clearInterval(interval);
    }, []);

    const getVoteBadge = (vote: string) => {
        if (vote === 'bull') return <span style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>🚀 상승전망</span>;
        if (vote === 'bear') return <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>📉 하락전망</span>;
        return <span style={{ backgroundColor: '#f3f4f6', color: '#4b5563', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>👀 관망</span>;
    };

    return (
        <div style={{ backgroundColor: 'white', border: '1px solid #e1e3e8', borderRadius: '12px', padding: '20px', marginTop: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#1a1b1e', margin: 0 }}>
                    🔥 실시간 시장 톡 <span style={{ fontSize: '0.8rem', fontWeight: 400, color: '#76777d', marginLeft: '8px' }}>(Community Feed)</span>
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <div style={{ width: '8px', height: '8px', backgroundColor: '#22c55e', borderRadius: '50%', animation: 'pulse 2s infinite' }}></div>
                    <span style={{ fontSize: '0.8rem', color: '#76777d', fontWeight: 600 }}>Live 투표 참여중</span>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
                {comments.map((comment) => (
                    <div key={comment.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '16px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #e9ecef' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ fontWeight: 800, fontSize: '0.9rem', color: '#2e2f32' }}>[{comment.complex_name}]</span>
                                {getVoteBadge(comment.vote)}
                            </div>
                            <span style={{ fontSize: '0.75rem', color: '#adb5bd' }}>
                                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true, locale: ko })}
                            </span>
                        </div>
                        <p style={{ fontSize: '0.85rem', color: '#495057', margin: 0, lineHeight: 1.5, wordBreak: 'keep-all' }}>
                            {comment.content}
                        </p>
                    </div>
                ))}
            </div>
            {comments.length === 0 && (
                <div style={{ padding: '20px', textAlign: 'center', color: '#adb5bd', fontSize: '0.9rem' }}>
                    아직 등록된 의견이 없습니다. 첫 번째 의견을 남겨보세요!
                </div>
            )}
        </div>
    );
}
