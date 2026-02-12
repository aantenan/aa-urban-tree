import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/errorHandler';
import { apiJson } from '../services/api';
import { Button, Form, Input } from '../components/ui';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setToken, setUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/dashboard';
  const successMessage = location.state?.message;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await apiJson('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (res.token) {
        setToken(res.token);
        if (res.user) setUser(res.user);
        navigate(from, { replace: true });
      }
    } catch (err) {
      // Security-conscious: same message for wrong email or wrong password
      if (err?.status === 429) {
        setError('Too many failed attempts. Your account is locked for 15 minutes. Try again later.');
      } else {
        setError(getErrorMessage(err) || 'Invalid email or password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ paddingTop: '2rem', maxWidth: 420, margin: '0 auto' }}>
      <h2>Sign in</h2>
      {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
      {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
      <Form onSubmit={handleSubmit}>
        <Input
          name="email"
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />
        <Input
          name="password"
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />
        <Button type="submit" disabled={loading} style={{ marginTop: '1rem' }}>
          {loading ? 'Signing in…' : 'Sign in'}
        </Button>
      </Form>
      <p style={{ marginTop: '1rem' }}>
        <Link to="/forgot-password">Forgot password?</Link>
      </p>
      <p>
        Don’t have an account? <Link to="/register">Create account</Link>
      </p>
    </div>
  );
}
