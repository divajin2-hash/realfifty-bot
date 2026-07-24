"use client";
import React, { useState } from 'react';

export default function SearchInput() {
    const [val, setVal] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setVal(e.target.value);
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('kb50_search', { detail: e.target.value }));
        }
    };

    return (
        <div style={{ position: 'relative', width: '100%', marginBottom: '16px' }}>
            <span style={{ position: 'absolute', left: '16px', top: '12px', opacity: 0.6 }}>🔍</span>
            <input
                type="text"
                placeholder="단지명 검색..."
                value={val}
                onChange={handleChange}
                style={{
                    width: '100%',
                    padding: '12px 16px 12px 42px',
                    borderRadius: '8px',
                    border: '1px solid #454d60',
                    background: '#191c1e',
                    color: '#ffffff',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    outline: 'none',
                    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)'
                }}
            />
        </div>
    );
}
