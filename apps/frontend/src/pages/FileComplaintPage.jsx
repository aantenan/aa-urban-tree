import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitComplaint, getCategories } from '../services/complaintApi';
import { getErrorMessage } from '../utils/errorHandler';
import { Button } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function FileComplaintPage() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState({ categories: [], category_departments: {} });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    subject: '',
    description: '',
    category: 'other',
    location_or_reference: '',
  });

  useEffect(() => {
    let cancelled = false;
    getCategories()
      .then((data) => {
        if (!cancelled) setCategories({ categories: data.categories || [], category_departments: data.category_departments || {} });
      })
      .catch((err) => { if (!cancelled) setError(getErrorMessage(err)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (!form.subject.trim() || !form.description.trim()) {
      setError('Subject and description are required.');
      return;
    }
    setSubmitting(true);
    submitComplaint({
      subject: form.subject.trim(),
      description: form.description.trim(),
      category: form.category || 'other',
      location_or_reference: form.location_or_reference.trim() || null,
    })
      .then((complaint) => {
        navigate(`/complaints/${complaint.id}`, { state: { message: 'Complaint submitted. You can track its status here.' } });
      })
      .catch((err) => {
        setError(getErrorMessage(err));
        setSubmitting(false);
      });
  };

  if (loading) return <div className="container"><LoadingSpinner /></div>;

  return (
    <div className="container">
      <div className="content-card">
        <h2 style={{ margin: 0 }}>File a complaint</h2>
        <p style={{ margin: '0.5rem 0 0' }}>Submit a citizen complaint. We’ll route it to the right department and you can track its status.</p>

        {error && <p role="alert" style={{ color: 'crimson', marginTop: '1rem' }}>{error}</p>}

        <form onSubmit={handleSubmit} style={{ marginTop: '1.5rem', maxWidth: '32rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="complaint-subject">Subject *</label>
            <input
              id="complaint-subject"
              type="text"
              value={form.subject}
              onChange={(e) => setForm((f) => ({ ...f, subject: e.target.value }))}
              maxLength={255}
              required
              style={{ display: 'block', width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="complaint-category">Category</label>
            <select
              id="complaint-category"
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              style={{ display: 'block', width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            >
              {categories.categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="complaint-description">Description *</label>
            <textarea
              id="complaint-description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={4}
              required
              style={{ display: 'block', width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="complaint-location">Location or reference (optional)</label>
            <input
              id="complaint-location"
              type="text"
              value={form.location_or_reference}
              onChange={(e) => setForm((f) => ({ ...f, location_or_reference: e.target.value }))}
              style={{ display: 'block', width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </div>
          <div>
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? 'Submitting…' : 'Submit complaint'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
