import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Renders children only when authenticated; otherwise redirects to login (or home).
 */
export function ProtectedRoute({ children, redirectTo = '/' }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }
  return children;
}
