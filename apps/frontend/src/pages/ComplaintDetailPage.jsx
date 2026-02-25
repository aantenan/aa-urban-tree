import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getComplaint } from '../services/complaintApi';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function ComplaintDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    getComplaint(id)
      .then((data) => { if (!cancelled) setComplaint(data); })
      .catch((err) => { if (!cancelled) setError(getErrorMessage(err)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id]);

  if (loading) return <div className="container"><LoadingSpinner /></div>;
  if (error || !complaint) {
    return (
      <div className="container">
        <p role="alert" style={{ color: 'crimson' }}>{error || 'Complaint not found.'}</p>
        <Link to="/complaints">Back to my complaints</Link>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="content-card">
        <p><Link to="/complaints">← My complaints</Link></p>
        <h2 style={{ margin: '0.5rem 0 0' }}>{complaint.subject}</h2>
        <div style={{ marginTop: '0.5rem', color: '#555' }}>
          Category: {complaint.category} · Department: {complaint.department || '—'} · Status: <strong>{complaint.status}</strong>
        </div>
        <div style={{ marginTop: '1rem' }}>{complaint.description}</div>
        {complaint.location_or_reference && (
          <p style={{ marginTop: '0.5rem' }}><strong>Location/reference:</strong> {complaint.location_or_reference}</p>
        )}
        {complaint.resolution_notes && (
          <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#f5f5f5', borderRadius: 4 }}>
            <strong>Resolution notes:</strong> {complaint.resolution_notes}
          </div>
        )}
        <p style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
          Submitted {complaint.created_at ? new Date(complaint.created_at).toLocaleString() : ''}
          {complaint.updated_at && ` · Last updated ${new Date(complaint.updated_at).toLocaleString()}`}
        </p>
      </div>
    </div>
  );
}
