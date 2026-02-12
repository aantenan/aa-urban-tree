import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function HomePage() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div style={{ padding: '2rem', maxWidth: 800, margin: '0 auto' }}>
      <h1>Urban Tree Grant Application</h1>
      <p>Apply for urban tree planting grants.</p>
      <p>
        <Link to="/listing">View program information and resources</Link>
      </p>
      {isAuthenticated ? (
        <div>
          <Link to="/dashboard">Dashboard</Link>
          <button type="button" onClick={logout} style={{ marginLeft: '1rem' }}>
            Sign out
          </button>
        </div>
      ) : (
        <>
          <Link to="/login">Sign in</Link>
          {' · '}
          <Link to="/register">Create account</Link>
        </>
      )}
    </div>
  );
}
