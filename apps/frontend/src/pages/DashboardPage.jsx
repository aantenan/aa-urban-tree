import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiJson } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    apiJson('/api/v1/applications')
      .then((res) => {
        if (cancelled) return;
        const data = res?.data ?? res;
        setApplications(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="container" style={{ paddingTop: '2rem', maxWidth: 800, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h2 style={{ margin: 0 }}>Dashboard</h2>
        <Button type="button" variant="secondary" onClick={() => { logout(); navigate('/', { replace: true }); }}>
          Sign out
        </Button>
      </div>
      <p>{user ? `Welcome, ${user.email || 'User'}` : 'Welcome.'}</p>

      <section style={{ marginTop: '1.5rem' }}>
        <h3>Applications</h3>
        {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
        {loading && <LoadingSpinner />}
        {!loading && !error && (
          <>
            <p>
              <Link to="/dashboard/application">
                <Button type="button" variant="primary">Start new application</Button>
              </Link>
            </p>
            {applications.length === 0 ? (
              <p>You have no applications yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {applications.map((app) => (
                  <li key={app.id} style={{ marginBottom: '0.5rem' }}>
                    <Link to={`/dashboard/application/${app.id}`}>
                      Application {app.id.slice(0, 8)}… — {app.status}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>
    </div>
  );
}
