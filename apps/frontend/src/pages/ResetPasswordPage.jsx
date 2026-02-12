import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getErrorMessage } from '../utils/errorHandler';
import { apiJson } from '../services/api';
import { passwordStrength } from '../utils/validation';
import { Button, Form, Input } from '../components/ui';
import { PasswordStrengthIndicator } from '../components/PasswordStrengthIndicator';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const pwStrength = passwordStrength(password);
  const match = password && confirm && password === confirm;
  const matchError = confirm && password !== confirm ? 'Passwords do not match' : null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!pwStrength.valid || !match) return;
    if (!token) {
      setError('Invalid or missing reset link. Request a new one from the forgot password page.');
      return;
    }
    setLoading(true);
    try {
      await apiJson('/api/v1/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ token, new_password: password }),
      });
      setSuccess(true);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="container" style={{ paddingTop: '2rem', maxWidth: 420, margin: '0 auto' }}>
        <h2>Password reset</h2>
        <p>Your password has been updated. You can now sign in with your new password.</p>
        <p><Link to="/login"><Button type="button">Sign in</Button></Link></p>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="container" style={{ paddingTop: '2rem', maxWidth: 420, margin: '0 auto' }}>
        <h2>Invalid link</h2>
        <p>This reset link is invalid or has expired. <Link to="/forgot-password">Request a new one</Link>.</p>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '2rem', maxWidth: 420, margin: '0 auto' }}>
      <h2>Set new password</h2>
      {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
      <Form onSubmit={handleSubmit}>
        <Input
          name="password"
          label="New password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={!pwStrength.valid && password ? pwStrength.message : null}
          required
          autoComplete="new-password"
        />
        <PasswordStrengthIndicator password={password} />
        <Input
          name="confirm"
          label="Confirm new password"
          type="password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          error={matchError}
          required
          autoComplete="new-password"
        />
        <Button
          type="submit"
          disabled={loading || !pwStrength.valid || !match}
          style={{ marginTop: '1rem' }}
        >
          {loading ? 'Updating…' : 'Update password'}
        </Button>
      </Form>
      <p style={{ marginTop: '1rem' }}><Link to="/login">Back to sign in</Link></p>
    </div>
  );
}
