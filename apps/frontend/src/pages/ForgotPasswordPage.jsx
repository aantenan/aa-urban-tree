import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { getErrorMessage } from '../utils/errorHandler';
import { apiJson } from '../services/api';
import { Button, Form, Input } from '../components/ui';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await apiJson('/api/v1/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email: email.trim() }),
      });
      setSent(true);
    } catch (err) {
      if (err?.status === 501) {
        setError('Password reset is not available in this environment.');
      } else {
        setError(getErrorMessage(err));
      }
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="container" style={{ paddingTop: '2rem', maxWidth: 420, margin: '0 auto' }}>
        <h2>Check your email</h2>
        <p>
          If an account exists for that email, we’ve sent instructions to reset your password.
          Check your inbox and follow the link.
        </p>
        <p><Link to="/login">Back to sign in</Link></p>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '2rem', maxWidth: 420, margin: '0 auto' }}>
      <h2>Forgot password</h2>
      <p>Enter your email and we’ll send you a link to reset your password.</p>
      {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
      <Form onSubmit={handleSubmit}>
        <Input
          name="email"
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Button type="submit" disabled={loading} style={{ marginTop: '1rem' }}>
          {loading ? 'Sending…' : 'Send reset link'}
        </Button>
      </Form>
      <p style={{ marginTop: '1rem' }}>
        <Link to="/login">Back to sign in</Link>
      </p>
    </div>
  );
}
