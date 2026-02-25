import React, { useState, useEffect } from 'react';
import { apiFetch } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

const getBaseUrl = () => import.meta.env.VITE_API_BASE_URL || '';

export function PublicDataQueryPage() {
  const [suggestions, setSuggestions] = useState({ suggestions: [], description: '' });
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  useEffect(() => {
    const base = getBaseUrl().replace(/\/$/, '');
    fetch(`${base}/api/public/data/suggestions`)
      .then((r) => r.json())
      .then((data) => {
        const d = data?.data ?? data;
        setSuggestions({ suggestions: d?.suggestions ?? [], description: d?.description ?? '' });
      })
      .catch(() => setSuggestions({ suggestions: [], description: '' }))
      .finally(() => setLoadingSuggestions(false));
  }, []);

  const runQuery = (q) => {
    const text = (q ?? query).trim();
    if (!text) return;
    setError('');
    setLoading(true);
    setResult(null);
    const base = getBaseUrl().replace(/\/$/, '');
    fetch(`${base}/api/public/data/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data?.success !== false) {
          setResult(data?.data ?? data);
          setError('');
        } else {
          setError(data?.message ?? 'Query failed');
          setResult(null);
        }
      })
      .catch((err) => {
        setError(getErrorMessage(err));
        setResult(null);
      })
      .finally(() => setLoading(false));
  };

  const rows = result?.rows ?? [];
  const keys = rows.length ? Object.keys(rows[0]) : [];

  return (
    <div className="container">
      <div className="content-card">
        <h2 style={{ margin: 0 }}>Public data</h2>
        <p style={{ margin: '0.5rem 0 0' }}>
          Ask questions about public program data (e.g. application counts, status, counties). No login required.
        </p>

        {loadingSuggestions && <LoadingSpinner />}
        {!loadingSuggestions && suggestions.suggestions?.length > 0 && (
          <div style={{ marginTop: '1rem' }}>
            <p style={{ margin: 0, fontWeight: 600 }}>Try asking:</p>
            <ul style={{ margin: '0.25rem 0 0', paddingLeft: '1.25rem' }}>
              {suggestions.suggestions.map((s, i) => (
                <li key={i}>
                  <button
                    type="button"
                    onClick={() => { setQuery(s); runQuery(s); }}
                    style={{ background: 'none', border: 'none', color: 'var(--link-color, #0066cc)', cursor: 'pointer', textDecoration: 'underline', padding: 0 }}
                  >
                    {s}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div style={{ marginTop: '1rem', maxWidth: '32rem' }}>
          <label htmlFor="data-query">Your question</label>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
            <input
              id="data-query"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && runQuery()}
              placeholder="e.g. How many applications are there?"
              style={{ flex: 1, padding: '0.5rem' }}
            />
            <Button type="button" variant="primary" onClick={() => runQuery()} disabled={loading}>
              {loading ? 'Querying…' : 'Query'}
            </Button>
          </div>
        </div>

        {error && <p role="alert" style={{ color: 'crimson', marginTop: '0.5rem' }}>{error}</p>}
        {loading && <LoadingSpinner />}

        {result && !loading && (
          <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
            <h3 style={{ margin: '0 0 0.5rem' }}>Results</h3>
            {rows.length === 0 ? (
              <p>No rows returned.</p>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #ddd' }}>
                    {keys.map((k) => (
                      <th key={k} style={{ textAlign: 'left', padding: '0.5rem' }}>{k}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
                      {keys.map((k) => (
                        <td key={k} style={{ padding: '0.5rem' }}>{String(row[k] ?? '')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
