import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/errorHandler';
import { apiJson } from '../services/api';
import { validate, required, email } from '../utils/validation';
import { passwordStrength } from '../utils/validation';
import { Button, Form, Input } from '../components/ui';
import { PasswordStrengthIndicator } from '../components/PasswordStrengthIndicator';

export function RegisterPage() {
  const [form, setForm] = useState({ email: '', password: '', name: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { setToken, setUser } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: null }));
  };

  const validateForm = () => {
    const emailErr = validate(form.email, [required, email]);
    const pwErr = required(form.password, 'Password') || (passwordStrength(form.password).valid ? null : 'Password does not meet complexity requirements');
    const next = { email: emailErr, password: pwErr || null };
    setErrors(next);
    return !next.email && !next.password;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!validateForm()) return;
    setLoading(true);
    try {
      const res = await apiJson('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: form.email.trim(),
          password: form.password,
          name: form.name.trim() || undefined,
        }),
      });
      if (res?.token) {
        setToken(res.token);
        if (res?.user) setUser(res.user);
        navigate('/dashboard', { replace: true });
      } else {
        navigate('/login', { replace: true, state: { message: 'Registration successful. Please sign in.' } });
      }
    } catch (err) {
      if (err?.status === 501) {
        setError('Registration is not available in this environment.');
      } else {
        setError(getErrorMessage(err));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ paddingTop: '2rem', maxWidth: 420, margin: '0 auto' }}>
      <h2>Create account</h2>
      {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}
      <Form onSubmit={handleSubmit}>
        <Input
          name="email"
          label="Email"
          type="email"
          value={form.email}
          onChange={handleChange}
          error={errors.email}
          required
        />
        <Input
          name="password"
          label="Password"
          type="password"
          value={form.password}
          onChange={handleChange}
          error={errors.password}
          required
          autoComplete="new-password"
        />
        <PasswordStrengthIndicator password={form.password} />
        <Input
          name="name"
          label="Name (optional)"
          value={form.name}
          onChange={handleChange}
        />
        <Button type="submit" disabled={loading} style={{ marginTop: '1rem' }}>
          {loading ? 'Creating account…' : 'Create account'}
        </Button>
      </Form>
      <p style={{ marginTop: '1rem' }}>
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </div>
  );
}
