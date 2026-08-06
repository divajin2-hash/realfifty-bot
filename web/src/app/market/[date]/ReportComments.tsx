"use client";

import React, { useState, useEffect } from 'react';

export default function ReportComments({ reportDate }: { reportDate: string }) {
    const [comments, setComments] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [nickname, setNickname] = useState('');
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchComments = async () => {
        try {
            const res = await fetch(`/api/comments?date=${reportDate}`);
            const data = await res.json();
            if (data.comments) setComments(data.comments);
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    useEffect(() => {
        fetchComments();
    }, [reportDate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!nickname.trim() || !content.trim()) return;

        setIsSubmitting(true);
        try {
            const res = await fetch('/api/comments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reportDate, nickname, content })
            });
            if (res.ok) {
                setContent('');
                fetchComments();
            }
        } catch (e) { console.error(e); }
        setIsSubmitting(false);
    };

    return (
        <div style={{ marginTop: '60px' }}>
            <h3 style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '16px', marginBottom: '24px', fontSize: '20px', fontWeight: 'bold' }}>
                트레이더 의견 ({comments.length})
            </h3>

            <div style={{ marginBottom: '40px' }}>
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px', backgroundColor: 'var(--card-bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-light)' }}>
                    <input
                        type="text"
                        placeholder="닉네임"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        style={{ flex: 1, padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border-light)', backgroundColor: 'var(--bg-main)', color: 'var(--text-dark)', outline: 'none' }}
                        required
                    />
                    <textarea
                        placeholder="오늘 시황에 대한 투자의견을 남겨주세요..."
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        rows={3}
                        style={{ padding: '10px 14px', borderRadius: '6px', border: '1px solid var(--border-light)', backgroundColor: 'var(--bg-main)', color: 'var(--text-dark)', outline: 'none', resize: 'vertical' }}
                        required
                    />
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        style={{ alignSelf: 'flex-end', backgroundColor: 'var(--text-dark)', color: 'var(--bg-main)', padding: '10px 24px', borderRadius: '6px', fontWeight: 'bold', border: 'none', cursor: isSubmitting ? 'not-allowed' : 'pointer' }}
                    >
                        {isSubmitting ? '등록 중...' : '의견 등록'}
                    </button>
                </form>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {loading ? <div style={{ color: 'var(--text-muted)' }}>댓글을 불러오는 중...</div> :
                    comments.length === 0 ? <div style={{ color: 'var(--text-muted)' }}>가장 먼저 의견을 남겨보세요!</div> :
                        comments.map(c => (
                            <div key={c.id} style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-light)', backgroundColor: 'var(--card-bg)', borderRadius: '12px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span style={{ fontWeight: 'bold', color: 'var(--accent-color)' }}>{c.user_name}</span>
                                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{new Date(c.created_at).toLocaleString()}</span>
                                </div>
                                <p style={{ margin: 0, lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>{c.content}</p>
                            </div>
                        ))
                }
            </div>
        </div>
    );
}
