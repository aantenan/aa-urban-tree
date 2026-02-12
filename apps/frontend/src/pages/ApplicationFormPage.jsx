import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiJson } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { Button, Form, Input } from '../components/ui';
import { LoadingSpinner } from '../components/LoadingSpinner';

const CONTACT_INITIAL = {
  organizationName: '',
  primaryContactName: '',
  email: '',
  phone: '',
};

function useApplicationForm(applicationId) {
  const [application, setApplication] = useState(null);
  const [formData, setFormData] = useState(CONTACT_INITIAL);
  const [status, setStatus] = useState('draft'); // 'draft' | 'saved' | 'loading' | 'error'
  const [loadError, setLoadError] = useState('');
  const [saveError, setSaveError] = useState('');

  const load = useCallback(async () => {
    if (!applicationId) {
      setApplication(null);
      setFormData(CONTACT_INITIAL);
      setStatus('draft');
      setLoadError('');
      return;
    }
    setStatus('loading');
    setLoadError('');
    try {
      const res = await apiJson(`/api/v1/applications/${applicationId}`);
      const data = res?.data ?? res;
      setApplication(data);
      setFormData({
        ...CONTACT_INITIAL,
        ...(data?.form_data?.contact || {}),
      });
      setStatus('draft');
    } catch (err) {
      setLoadError(getErrorMessage(err));
      setStatus('error');
    }
  }, [applicationId]);

  useEffect(() => {
    load();
  }, [load]);

  const save = useCallback(async () => {
    if (!applicationId) {
      setSaveError('Create an application first.');
      return;
    }
    setSaveError('');
    setStatus('loading');
    try {
      const res = await apiJson(`/api/v1/applications/${applicationId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          form_data: { contact: formData },
        }),
      });
      const data = res?.data ?? res;
      setApplication(data);
      setStatus('saved');
    } catch (err) {
      setSaveError(getErrorMessage(err));
      setStatus('draft');
    }
  }, [applicationId, formData]);

  return {
    application,
    formData,
    setFormData,
    status,
    loadError,
    saveError,
    save,
    reload: load,
  };
}

export function ApplicationFormPage() {
  const { id: applicationId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const {
    application,
    formData,
    setFormData,
    status,
    loadError,
    saveError,
    save,
    reload,
  } = useApplicationForm(applicationId);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    save();
  };

  const handleStartNew = async () => {
    try {
      const res = await apiJson('/api/v1/applications', { method: 'POST' });
      const data = res?.data ?? res;
      if (data?.id) navigate(`/dashboard/application/${data.id}`, { replace: true });
    } catch (err) {
      setSaveError(getErrorMessage(err));
    }
  };

  const validationErrors = {};
  if (formData.organizationName?.trim() === '') validationErrors.organizationName = 'Required';
  if (formData.primaryContactName?.trim() === '') validationErrors.primaryContactName = 'Required';
  if (formData.email?.trim() === '') validationErrors.email = 'Required';
  const canSubmit = !validationErrors.organizationName && !validationErrors.primaryContactName && !validationErrors.email;

  if (!isAuthenticated) return null;

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '2rem' }}>
      <header style={{ marginBottom: '1.5rem' }}>
        <h1>Grant Application</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <span
            className="form-status"
            aria-live="polite"
            style={{
              padding: '0.25rem 0.5rem',
              borderRadius: 4,
              background: status === 'saved' ? '#e8f5e9' : status === 'error' ? '#ffebee' : '#f5f5f5',
            }}
          >
            {status === 'loading' && 'Saving…'}
            {status === 'saved' && 'Saved'}
            {status === 'draft' && (application ? 'Draft' : 'New')}
            {status === 'error' && 'Error'}
          </span>
          {application?.id && (
            <Button type="button" variant="secondary" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
          )}
          {!applicationId && (
            <Button type="button" variant="primary" onClick={handleStartNew}>
              Start new application
            </Button>
          )}
        </div>
      </header>

      {loadError && (
        <div role="alert" style={{ color: 'crimson', marginBottom: '1rem' }}>
          {loadError}
          <Button type="button" variant="secondary" onClick={reload} style={{ marginLeft: '0.5rem' }}>
            Retry
          </Button>
        </div>
      )}

      {status === 'loading' && !formData.organizationName && applicationId ? (
        <LoadingSpinner />
      ) : (
        <Form onSubmit={handleSubmit} aria-label="Contact information">
          <section className="form-section" aria-labelledby="contact-heading">
            <h2 id="contact-heading">Contact Information</h2>
            <Input
              name="organizationName"
              label="Organization name"
              value={formData.organizationName}
              onChange={handleChange}
              error={validationErrors.organizationName}
              required
            />
            <Input
              name="primaryContactName"
              label="Primary contact name"
              value={formData.primaryContactName}
              onChange={handleChange}
              error={validationErrors.primaryContactName}
              required
            />
            <Input
              name="email"
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              error={validationErrors.email}
              required
            />
            <Input
              name="phone"
              label="Phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
            />
          </section>

          {saveError && (
            <p role="alert" style={{ color: 'crimson', marginBottom: '1rem' }}>
              {saveError}
            </p>
          )}

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
            <Button type="submit" disabled={!canSubmit || status === 'loading'}>
              {status === 'loading' ? 'Saving…' : 'Save'}
            </Button>
          </div>
        </Form>
      )}
    </div>
  );
}
