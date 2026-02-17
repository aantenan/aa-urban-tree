import React, { useCallback, useEffect, useState } from 'react';
import { apiJson } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import { validateContactForm, CONTACT_INITIAL } from '../utils/contactValidation';
import { useAutoSave } from '../hooks/useAutoSave';
import { US_STATES } from '../data/usStates';
import { MARYLAND_COUNTIES } from '../data/marylandCounties';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from './ui';
import { LoadingSpinner } from './LoadingSpinner';

const AUTO_SAVE_DELAY_MS = 1500;

/**
 * Contact information section: full field set, county dropdown from API,
 * client-side validation, auto-save, section completion from backend.
 * Follows backend contract: GET/PUT /api/v1/applications/{id}/contact-information.
 */
export function ContactInformationSection({ applicationId }) {
  const { user } = useAuth();
  const [formValues, setFormValues] = useState(() => ({
    ...CONTACT_INITIAL,
    ...(user ? {
      primary_contact_name: user.name || '',
      primary_contact_email: user.email || '',
    } : {}),
  }));
  const [counties, setCounties] = useState([]);
  const [countiesLoading, setCountiesLoading] = useState(true);
  const [contactLoading, setContactLoading] = useState(!!applicationId);
  const [loadError, setLoadError] = useState('');
  const [saveStatus, setSaveStatus] = useState('idle'); // idle | saving | saved | error
  const [apiError, setApiError] = useState('');
  const [sectionComplete, setSectionComplete] = useState(false);
  const [backendErrors, setBackendErrors] = useState(null);
  const [touched, setTouched] = useState({});

  // Fetch counties once; use Maryland fallback if API fails or returns empty
  useEffect(() => {
    let cancelled = false;
    apiJson('/api/v1/counties')
      .then((res) => {
        if (cancelled) return;
        const list = res?.data ?? res;
        const arr = Array.isArray(list) ? list : [];
        setCounties(arr.length > 0 ? arr : MARYLAND_COUNTIES);
      })
      .catch(() => {
        if (!cancelled) setCounties(MARYLAND_COUNTIES);
      })
      .finally(() => {
        if (!cancelled) setCountiesLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const loadContact = useCallback(() => {
    if (!applicationId) return;
    setContactLoading(true);
    setLoadError('');
    apiJson(`/api/v1/applications/${applicationId}/contact-information`)
      .then((res) => {
        const data = res?.data ?? res;
        const contact = data?.contact_information;
        const base = { ...CONTACT_INITIAL, ...(contact || {}) };
        if (user && !contact?.primary_contact_email) {
          base.primary_contact_name = base.primary_contact_name || user.name || '';
          base.primary_contact_email = base.primary_contact_email || user.email || '';
        }
        setFormValues(base);
        setSectionComplete(!!data?.section_complete);
        setBackendErrors(null);
      })
      .catch((err) => {
        setLoadError(getErrorMessage(err));
      })
      .finally(() => {
        setContactLoading(false);
      });
  }, [applicationId, user]);

  useEffect(() => {
    if (!applicationId) {
      setFormValues({
        ...CONTACT_INITIAL,
        ...(user ? { primary_contact_name: user.name || '', primary_contact_email: user.email || '' } : {}),
      });
      setSectionComplete(false);
      setContactLoading(false);
      return;
    }
    loadContact();
  }, [applicationId, loadContact, user]);

  const saveContact = useCallback(async (payload) => {
    if (!applicationId) return;
    setSaveStatus('saving');
    setApiError('');
    try {
      const res = await apiJson(`/api/v1/applications/${applicationId}/contact-information`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      const data = res?.data ?? res;
      setSectionComplete(!!data?.section_complete);
      setBackendErrors(data?.errors ?? null);
      setSaveStatus('saved');
    } catch (err) {
      setApiError(getErrorMessage(err));
      setSaveStatus('error');
    }
  }, [applicationId]);

  useAutoSave(formValues, saveContact, {
    delay: AUTO_SAVE_DELAY_MS,
    enabled: !!applicationId && !contactLoading,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleBlur = (e) => {
    setTouched((prev) => ({ ...prev, [e.target.name]: true }));
  };

  const clientErrors = validateContactForm(formValues);
  const getError = (key) => backendErrors?.[key] ?? (touched[key] ? clientErrors[key] : null);

  if (contactLoading && applicationId) {
    return (
      <section className="form-section contact-section" aria-labelledby="contact-heading">
        <h2 id="contact-heading">Contact Information</h2>
        <LoadingSpinner />
      </section>
    );
  }

  return (
    <section
      id="contact-information"
      className="form-section contact-section"
      aria-labelledby="contact-heading"
      aria-describedby="contact-status"
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <h2 id="contact-heading" style={{ margin: 0 }}>Contact Information</h2>
        <span
          id="contact-status"
          className="form-section__completion"
          aria-live="polite"
          role="status"
          style={{
            padding: '0.25rem 0.5rem',
            borderRadius: 4,
            fontSize: '0.875rem',
            background: sectionComplete ? '#e8f5e9' : '#fff3e0',
            color: sectionComplete ? '#1b5e20' : '#e65100',
          }}
        >
          {sectionComplete ? 'Section complete' : 'Incomplete'}
        </span>
        {saveStatus === 'saving' && (
          <span className="form-section__saving" aria-live="polite">
            Saving…
          </span>
        )}
        {saveStatus === 'saved' && (
          <span className="form-section__saved" aria-live="polite">
            Saved
          </span>
        )}
      </div>

      {loadError && (
        <p role="alert" className="form-section__error">
          {loadError}
          <Button type="button" variant="secondary" onClick={loadContact} style={{ marginLeft: '0.5rem' }}>
            Retry
          </Button>
        </p>
      )}
      {apiError && (
        <p role="alert" className="form-section__error">
          {apiError}
        </p>
      )}

      <div className="contact-section__grid">
        <div className="contact-section__block">
          <h3 className="contact-section__subheading">Organization</h3>
          <Input
            name="organization_name"
            label="Organization name"
            value={formValues.organization_name}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('organization_name')}
            required
            aria-required="true"
          />
        </div>

        <div className="contact-section__block">
          <h3 className="contact-section__subheading">Mailing address</h3>
          <Input
            name="address_line1"
            label="Street address"
            value={formValues.address_line1}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('address_line1')}
            required
          />
          <Input
            name="address_line2"
            label="Address line 2 (optional)"
            value={formValues.address_line2}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          <div className="contact-section__row contact-section__row--address">
            <div className="input-group contact-section__city-wrap">
              <label htmlFor="input-city" className="input-group__label">
                City <span className="input-group__required" aria-hidden="true">*</span>
              </label>
              <input
                id="input-city"
                name="city"
                type="text"
                value={formValues.city}
                onChange={handleChange}
                onBlur={handleBlur}
                required
                aria-invalid={!!getError('city')}
                aria-required="true"
                className={`input-group__input contact-section__city-input ${getError('city') ? 'input-group__input--error' : ''}`}
              />
              {getError('city') && (
                <span id="input-city-error" className="input-group__error" role="alert">{getError('city')}</span>
              )}
            </div>
            <div className="input-group">
              <label htmlFor="contact-state" className="input-group__label">
                State <span className="input-group__required" aria-hidden="true">*</span>
              </label>
              <select
                id="contact-state"
                name="state_code"
                value={formValues.state_code}
                onChange={handleChange}
                onBlur={handleBlur}
                aria-required="true"
                aria-invalid={!!getError('state_code')}
                className={`input-group__input ${getError('state_code') ? 'input-group__input--error' : ''}`}
              >
                {US_STATES.map((s) => (
                  <option key={s.code} value={s.code}>{s.name}</option>
                ))}
              </select>
              {getError('state_code') && (
                <span className="input-group__error" role="alert">{getError('state_code')}</span>
              )}
            </div>
            <Input
              name="zip_code"
              label="ZIP code"
              value={formValues.zip_code}
              onChange={handleChange}
              onBlur={handleBlur}
              error={getError('zip_code')}
              required
            />
          </div>
          <div className="input-group">
            <label htmlFor="contact-county" className="input-group__label">
              County <span className="input-group__required" aria-hidden="true">*</span>
            </label>
            <select
              id="contact-county"
              name="county"
              value={formValues.county}
              onChange={handleChange}
              onBlur={handleBlur}
              aria-required="true"
              aria-invalid={!!getError('county')}
              aria-describedby={getError('county') ? 'contact-county-error' : undefined}
              className={`input-group__input ${getError('county') ? 'input-group__input--error' : ''}`}
              disabled={countiesLoading}
            >
              <option value="">Select county</option>
              {counties
                .filter((c) => c.state_code === formValues.state_code || c.state_code === 'MD')
                .map((c) => (
                  <option key={c.id} value={c.name}>
                    {c.name}{c.state_code ? `, ${c.state_code}` : ''}
                  </option>
                ))}
            </select>
            {getError('county') && (
              <span id="contact-county-error" className="input-group__error" role="alert">
                {getError('county')}
              </span>
            )}
          </div>
        </div>

        <div className="contact-section__block">
          <h3 className="contact-section__subheading">Primary contact</h3>
          <Input
            name="primary_contact_name"
            label="Full name"
            value={formValues.primary_contact_name}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('primary_contact_name')}
            required
          />
          <Input
            name="primary_contact_title"
            label="Title (optional)"
            value={formValues.primary_contact_title}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          <Input
            name="primary_contact_email"
            label="Email"
            type="email"
            value={formValues.primary_contact_email}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('primary_contact_email')}
            required
            autoComplete="email"
          />
          <Input
            name="primary_contact_phone"
            label="Phone"
            type="tel"
            value={formValues.primary_contact_phone}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('primary_contact_phone')}
            autoComplete="tel"
          />
        </div>

        <div className="contact-section__block">
          <h3 className="contact-section__subheading">Alternate contact (optional)</h3>
          <Input
            name="alternate_contact_name"
            label="Full name"
            value={formValues.alternate_contact_name}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          <Input
            name="alternate_contact_title"
            label="Title"
            value={formValues.alternate_contact_title}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          <Input
            name="alternate_contact_email"
            label="Email"
            type="email"
            value={formValues.alternate_contact_email}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('alternate_contact_email')}
            autoComplete="email"
          />
          <Input
            name="alternate_contact_phone"
            label="Phone"
            type="tel"
            value={formValues.alternate_contact_phone}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('alternate_contact_phone')}
            autoComplete="tel"
          />
        </div>
      </div>
    </section>
  );
}
