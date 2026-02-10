import React from 'react';
import { useAuth } from '../context/AuthContext';

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div style={{ padding: '2rem', maxWidth: 800, margin: '0 auto' }}>
      <h2>Dashboard</h2>
      <p>{user ? `Welcome, ${user.email || 'User'}` : 'Welcome.'}</p>
      <p>Application management will appear here.</p>
    </div>
  );
}
