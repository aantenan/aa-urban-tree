import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listAllComplaints, updateComplaintStatus, getCategories } from '../services/complaintApi';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function AdminComplaintsPage() {
  const [data, setData] = useState({ items: [], total: 0 });
  const [categories, setCategories] = useState({ categories: [], statuses: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [updatingId, setUpdatingId] = useState(null);

  const load = () => {
    setLoading(true);
    setError('');
    Promise.all([
      listAllComplaints({ status: statusFilter || undefined, category: categoryFilter || undefined }),
      getCategories(),
    ])
      .then(([listData, catData]) => {
        setData({
          items: listData?.items ?? listData ?? [],
          total: listData?.total ?? (Array.isArray(listData) ? listData.length : 0),
        });
        setCategories({
          categories: catData?.categories ?? [],
          statuses: catData?.statuses ?? [],
        });
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [statusFilter, categoryFilter]);

  const handleStatusChange = (complaintId, newStatus) => {
    setUpdatingId(complaintId);
    updateComplaintStatus(complaintId, { status: newStatus })
      .then(() => load())
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setUpdatingId(null));
  };

  return (
    <div className="container">
      <div className="content-card">
        <h2 style={{ margin: 0 }}>Complaint management</h2>
        <p style={{ margin: '0.5rem 0 0' }}>View and manage all citizen complaints.</p>

        <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <label>
            Status:{' '}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ padding: '0.25rem' }}
            >
              <option value="">All</option>
              {categories.statuses.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </label>
          <label>
            Category:{' '}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              style={{ padding: '0.25rem' }}
            >
              <option value="">All</option>
              {categories.categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
        </div>

        {error && <p role="alert" style={{ color: 'crimson', marginTop: '0.5rem' }}>{error}</p>}
        {loading && <LoadingSpinner />}

        {!loading && (
          <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #ddd' }}>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Subject</th>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Category</th>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Status</th>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Created</th>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((c) => (
                  <tr key={c.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '0.5rem' }}>
                      <Link to={`/complaints/${c.id}`}>{c.subject}</Link>
                    </td>
                    <td style={{ padding: '0.5rem' }}>{c.category}</td>
                    <td style={{ padding: '0.5rem' }}>{c.status}</td>
                    <td style={{ padding: '0.5rem' }}>{c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <select
                        value={c.status}
                        onChange={(e) => handleStatusChange(c.id, e.target.value)}
                        disabled={updatingId === c.id}
                        style={{ padding: '0.25rem' }}
                      >
                        {categories.statuses.map((s) => <option key={s} value={s}>{s}</option>)}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {data.items.length === 0 && <p style={{ marginTop: '0.5rem' }}>No complaints match the filters.</p>}
          </div>
        )}
      </div>
    </div>
  );
}
