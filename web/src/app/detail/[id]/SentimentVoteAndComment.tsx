"use client";
import React, { useState, useEffect } from 'react';
import { supabase } from '@/utils/supabase';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

interface SentimentVoteAndCommentProps {
    complexId: string;
    complexName: string;
}

export default function SentimentVoteAndComment({ complexId, complexName }: SentimentVoteAndCommentProps) {
    const [comments, setComments] = useState<any[]>([]);
    const [authorName, setAuthorName] = useState('');
    const [vote, setVote] = useState<'bull' | 'bear' | 'neutral' | null>(null);
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        fetchComments();
    }, [complexId]);

    const fetchComments = async () => {
        const { data, error } = await supabase
            .from('community_comments')
            .select('*')
            .eq('complex_id', complexId)
            .order('created_at', { ascending: false })
            .limit(20);

        if (data && !error) {
            setComments(data);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!vote) return alert('상승 또는 하락 투표를 먼저 선택해주세요!');
        if (!authorName.trim()) return alert('닉네임을 입력해주세요 (최대 8자)');
        if (!content.trim()) return alert('의견을 작성해주세요.');

        setIsSubmitting(true);
        const { error } = await supabase.from('community_comments').insert({
            complex_id: complexId,
            author_name: authorName.substring(0, 8),
            vote: vote,
            content: content.trim(),
            is_bot: false,
            persona_type: 'real_user'
        });

        setIsSubmitting(false);

        if (!error) {
            setVote(null);
            setContent('');
            // Keep nickname in state for convenience
            fetchComments();
        } else {
            alert('의견 등록에 실패했습니다.');
            console.error(error);
        }
    };

    const getVoteBadge = (v: string) => {
        if (v === 'bull') return <span style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700 }}>🚀 상승전망</span>;
        if (v === 'bear') return <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700 }}>📉 하락전망</span>;
        return <span style={{ backgroundColor: '#f3f4f6', color: '#4b5563', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700 }}>👀 관망</span>;
    };

    return (
        <div style={{ marginTop: '24px', backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e1e3e8', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '20px' }}>💭 {complexName} 토론방</h2>

            {/* 글쓰기 폼 */}
            <form onSubmit={handleSubmit} style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '32px' }}>
                <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, marginBottom: '8px', color: '#495057' }}>1. {complexName} 전망 예측하기</label>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button type="button" onClick={() => setVote('bull')} style={{ flex: 1, padding: '12px', borderRadius: '6px', border: vote === 'bull' ? '2px solid #ef4444' : '1px solid #dee2e6', backgroundColor: vote === 'bull' ? '#fef2f2' : 'white', cursor: 'pointer', fontWeight: 700, transition: 'all 0.2s', color: vote === 'bull' ? '#b91c1c' : '#495057' }}>
                            🚀 오를 것 같다
                        </button>
                        <button type="button" onClick={() => setVote('bear')} style={{ flex: 1, padding: '12px', borderRadius: '6px', border: vote === 'bear' ? '2px solid #0ea5e9' : '1px solid #dee2e6', backgroundColor: vote === 'bear' ? '#f0f9ff' : 'white', cursor: 'pointer', fontWeight: 700, transition: 'all 0.2s', color: vote === 'bear' ? '#0369a1' : '#495057' }}>
                            📉 내릴 것 같다
                        </button>
                    </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, marginBottom: '8px', color: '#495057' }}>2. 닉네임 (최대 8자, 비회원 가능)</label>
                    <input
                        type="text"
                        maxLength={8}
                        value={authorName}
                        onChange={(e) => setAuthorName(e.target.value)}
                        placeholder="예: 강남가즈아"
                        style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid #dee2e6', fontSize: '0.9rem' }}
                    />
                </div>

                <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, marginBottom: '8px', color: '#495057' }}>3. 의견 작성</label>
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        rows={3}
                        placeholder="솔직한 의견을 남겨주세요."
                        style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid #dee2e6', fontSize: '0.9rem', resize: 'vertical' }}
                    />
                </div>

                <button type="submit" disabled={isSubmitting} style={{ width: '100%', padding: '14px', borderRadius: '6px', border: 'none', backgroundColor: '#131b2e', color: 'white', fontWeight: 800, cursor: isSubmitting ? 'not-allowed' : 'pointer', fontSize: '1rem' }}>
                    {isSubmitting ? '등록 중...' : '투표 및 의견 등록하기'}
                </button>
            </form>

            {/* 댓글 목록 */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 800, paddingBottom: '12px', borderBottom: '2px solid #f1f3f5' }}>최신 실시간 의견 ({comments.length}건)</h3>

                {comments.map((comment) => (
                    <div key={comment.id} style={{ padding: '16px', borderBottom: '1px solid #f1f3f5' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                {getVoteBadge(comment.vote)}
                                <span style={{ fontWeight: 800, fontSize: '0.9rem', color: '#131b2e' }}>{comment.author_name || '익명유저'}</span>
                                {comment.is_bot === false && (
                                    <span style={{ fontSize: '0.65rem', backgroundColor: '#e9ecef', padding: '2px 6px', borderRadius: '4px', color: '#adb5bd', fontWeight: 600 }}>유저</span>
                                )}
                            </div>
                            <span style={{ fontSize: '0.75rem', color: '#adb5bd' }}>
                                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true, locale: ko })}
                            </span>
                        </div>
                        <p style={{ margin: 0, fontSize: '0.9rem', color: '#495057', lineHeight: 1.5, wordBreak: 'keep-all' }}>
                            {comment.content}
                        </p>
                    </div>
                ))}

                {comments.length === 0 && (
                    <div style={{ padding: '40px 20px', textAlign: 'center', color: '#adb5bd', fontSize: '0.95rem' }}>
                        아직 작성된 의견이 없습니다. 첫 번째 의견을 남겨보세요!
                    </div>
                )}
            </div>
        </div>
    )
}
