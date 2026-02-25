import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listMyComplaints } from '../services/complaintApi';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function ComplaintsPage() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    listMyComplaints()
      .then((data) => {
        if (!cancelled) setComplaints(Array.isArray(data) ? data : []);
      })
      .catch((err) => { if (!cancelled) setError(getErrorMessage(err)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="container">
      <div className="content-card">
        <h2 style={{ margin: 0 }}>My complaints</h2>
        <p style={{ margin: '0.5rem 0 0' }}>View and track your submitted complaints.</p>

        <section style={{ marginTop: '1.5rem' }}>
          <p>
            <Link to="/complaints/file">
              <Button type="button" variant="primary">File a new complaint</Button>
            </Link>
          </p>
          {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
          {loading && <LoadingSpinner />}
          {!loading && !error && (
            complaints.length === 0 ? (
              <p>You have not submitted any complaints yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {complaints.map((c) => (
                  <li key={c.id} style={{ marginBottom: '0.75rem', padding: '0.75rem', border: '1px solid #ddd', borderRadius: 4 }}>
                    <Link to={`/complaints/${c.id}`} style={{ fontWeight: 600 }}>
                      {c.subject}
                    </Link>
                    <div style={{ fontSize: '0.9rem', color: '#555', marginTop: '0.25rem' }}>
                      {c.category} · {c.status} · {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                    </div>
                  </li>
                ))}
              </ul>
            )
          )}
        </section>
      </div>
    </div>
  );
}
