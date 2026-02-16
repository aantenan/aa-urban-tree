import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui';

export function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="container">
      <div className="content-card">
        <h1 className="home-title">Welcome to the Urban Tree Grant Program</h1>
        <p className="home-lead">
          Apply for urban tree planting grants. Find program information, eligibility, and resources in one place.
        </p>
        <p>
          <Link to="/listing" className="home-link">
            View program information and resources
          </Link>
        </p>
        {isAuthenticated ? (
          <p style={{ marginTop: '1rem' }}>
            <Link to="/dashboard">
              <Button type="button" variant="primary">Go to Applications</Button>
            </Link>
          </p>
        ) : (
          <p style={{ marginTop: '1rem' }}>
            <Link to="/login" className="home-link">Log in</Link>
            {' · '}
            <Link to="/register" className="home-link">Register</Link>
          </p>
        )}
      </div>
    </div>
  );
}
