import React, { useCallback, useEffect, useState } from 'react';
import { apiJson } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import {
  validateProjectForm,
  PROJECT_INITIAL,
  DESCRIPTION_MAX,
} from '../utils/projectValidation';
import { useAutoSave } from '../hooks/useAutoSave';
import { Button, Input } from './ui';
import { DatePicker } from './DatePicker';
import { LoadingSpinner } from './LoadingSpinner';

const AUTO_SAVE_DELAY_MS = 1500;

/**
 * Project information section: form with site address, ownership, type,
 * acreage, tree count, timeline, description. Auto-save, section completion from backend.
 */
export function ProjectInformationSection({ applicationId }) {
  const [formValues, setFormValues] = useState(PROJECT_INITIAL);
  const [siteOwnershipOptions, setSiteOwnershipOptions] = useState([]);
  const [projectTypeOptions, setProjectTypeOptions] = useState([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [projectLoading, setProjectLoading] = useState(!!applicationId);
  const [loadError, setLoadError] = useState('');
  const [saveStatus, setSaveStatus] = useState('idle');
  const [apiError, setApiError] = useState('');
  const [sectionComplete, setSectionComplete] = useState(false);
  const [backendErrors, setBackendErrors] = useState(null);
  const [touched, setTouched] = useState({});

  const ownershipCodes = siteOwnershipOptions.map((o) => o.code);
  const projectTypeCodes = projectTypeOptions.map((o) => o.code);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      apiJson('/api/v1/site-ownership').then((r) => r?.data ?? r),
      apiJson('/api/v1/project-types').then((r) => r?.data ?? r),
    ])
      .then(([ownership, types]) => {
        if (cancelled) return;
        setSiteOwnershipOptions(Array.isArray(ownership) ? ownership : []);
        setProjectTypeOptions(Array.isArray(types) ? types : []);
      })
      .catch(() => {
        if (!cancelled) {
          setSiteOwnershipOptions([]);
          setProjectTypeOptions([]);
        }
      })
      .finally(() => {
        if (!cancelled) setOptionsLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const loadProject = useCallback(() => {
    if (!applicationId) return;
    setProjectLoading(true);
    setLoadError('');
    apiJson(`/api/v1/applications/${applicationId}/project-information`)
      .then((res) => {
        const data = res?.data ?? res;
        const project = data?.project_information;
        const raw = project || {};
        setFormValues({
          ...PROJECT_INITIAL,
          project_name: raw.project_name ?? '',
          site_address_line1: raw.site_address_line1 ?? '',
          site_address_line2: raw.site_address_line2 ?? '',
          site_city: raw.site_city ?? '',
          site_state_code: raw.site_state_code ?? '',
          site_zip_code: raw.site_zip_code ?? '',
          site_ownership: raw.site_ownership ?? '',
          project_type: raw.project_type ?? '',
          acreage: raw.acreage != null ? String(raw.acreage) : '',
          tree_count: raw.tree_count != null ? String(raw.tree_count) : '',
          start_date: raw.start_date ?? '',
          completion_date: raw.completion_date ?? '',
          description: raw.description ?? '',
        });
        setSectionComplete(!!data?.section_complete);
        setBackendErrors(null);
      })
      .catch((err) => {
        setLoadError(getErrorMessage(err));
      })
      .finally(() => {
        setProjectLoading(false);
      });
  }, [applicationId]);

  useEffect(() => {
    if (!applicationId) {
      setFormValues(PROJECT_INITIAL);
      setSectionComplete(false);
      setProjectLoading(false);
      return;
    }
    loadProject();
  }, [applicationId, loadProject]);

  const saveProject = useCallback(async (payload) => {
    if (!applicationId) return;
    setSaveStatus('saving');
    setApiError('');
    const acreage = payload.acreage === '' || payload.acreage == null ? null : Number(payload.acreage);
    const treeCount = payload.tree_count === '' || payload.tree_count == null ? null : Math.floor(Number(payload.tree_count));
    const body = {
      ...payload,
      acreage: Number.isFinite(acreage) ? acreage : null,
      tree_count: Number.isInteger(treeCount) ? treeCount : null,
    };
    try {
      const res = await apiJson(`/api/v1/applications/${applicationId}/project-information`, {
        method: 'PUT',
        body: JSON.stringify(body),
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

  useAutoSave(formValues, saveProject, {
    delay: AUTO_SAVE_DELAY_MS,
    enabled: !!applicationId && !projectLoading,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleBlur = (e) => {
    setTouched((prev) => ({ ...prev, [e.target.name]: true }));
  };

  const clientErrors = validateProjectForm(formValues, {
    siteOwnershipCodes: ownershipCodes,
    projectTypeCodes,
  });
  const getError = (key) => backendErrors?.[key] ?? (touched[key] ? clientErrors[key] : null);

  if (projectLoading && applicationId) {
    return (
      <section className="form-section project-section" aria-labelledby="project-heading">
        <h2 id="project-heading">Project Information</h2>
        <LoadingSpinner />
      </section>
    );
  }

  const descriptionLen = (formValues.description || '').length;

  return (
    <section
      id="project-information"
      className="form-section project-section"
      aria-labelledby="project-heading"
      aria-describedby="project-status"
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <h2 id="project-heading" style={{ margin: 0 }}>Project Information</h2>
        <span
          id="project-status"
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
        {saveStatus === 'saving' && <span className="form-section__saving" aria-live="polite">Saving…</span>}
        {saveStatus === 'saved' && <span className="form-section__saved" aria-live="polite">Saved</span>}
      </div>

      {loadError && (
        <p role="alert" className="form-section__error">
          {loadError}
          <Button type="button" variant="secondary" onClick={loadProject} style={{ marginLeft: '0.5rem' }}>
            Retry
          </Button>
        </p>
      )}
      {apiError && (
        <p role="alert" className="form-section__error">{apiError}</p>
      )}

      <div className="project-section__grid">
        <div className="project-section__block">
          <h3 className="project-section__subheading">Project details</h3>
          <Input
            name="project_name"
            label="Project name"
            value={formValues.project_name}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('project_name')}
            required
          />
        </div>

        <div className="project-section__block">
          <h3 className="project-section__subheading">Site address</h3>
          <Input
            name="site_address_line1"
            label="Street address"
            value={formValues.site_address_line1}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('site_address_line1')}
            required
          />
          <Input
            name="site_address_line2"
            label="Address line 2 (optional)"
            value={formValues.site_address_line2}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          <div className="contact-section__row">
            <Input
              name="site_city"
              label="City"
              value={formValues.site_city}
              onChange={handleChange}
              onBlur={handleBlur}
              error={getError('site_city')}
              required
            />
            <Input
              name="site_state_code"
              label="State"
              value={formValues.site_state_code}
              onChange={handleChange}
              onBlur={handleBlur}
              error={getError('site_state_code')}
              required
              placeholder="e.g. NY"
            />
            <Input
              name="site_zip_code"
              label="ZIP code"
              value={formValues.site_zip_code}
              onChange={handleChange}
              onBlur={handleBlur}
              error={getError('site_zip_code')}
              required
            />
          </div>
        </div>

        <div className="project-section__block">
          <h3 className="project-section__subheading">Ownership and type</h3>
          <div className="input-group">
            <label htmlFor="project-site-ownership" className="input-group__label">
              Site ownership <span className="input-group__required" aria-hidden="true">*</span>
            </label>
            <select
              id="project-site-ownership"
              name="site_ownership"
              value={formValues.site_ownership}
              onChange={handleChange}
              onBlur={handleBlur}
              aria-required="true"
              aria-invalid={!!getError('site_ownership')}
              aria-describedby={getError('site_ownership') ? 'project-site-ownership-error' : undefined}
              className={`input-group__input ${getError('site_ownership') ? 'input-group__input--error' : ''}`}
              disabled={optionsLoading}
            >
              <option value="">Select ownership</option>
              {siteOwnershipOptions.map((o) => (
                <option key={o.id} value={o.code}>{o.label}</option>
              ))}
            </select>
            {getError('site_ownership') && (
              <span id="project-site-ownership-error" className="input-group__error" role="alert">
                {getError('site_ownership')}
              </span>
            )}
          </div>
          <div className="input-group">
            <label htmlFor="project-type" className="input-group__label">
              Project type <span className="input-group__required" aria-hidden="true">*</span>
            </label>
            <select
              id="project-type"
              name="project_type"
              value={formValues.project_type}
              onChange={handleChange}
              onBlur={handleBlur}
              aria-required="true"
              aria-invalid={!!getError('project_type')}
              aria-describedby={getError('project_type') ? 'project-type-error' : undefined}
              className={`input-group__input ${getError('project_type') ? 'input-group__input--error' : ''}`}
              disabled={optionsLoading}
            >
              <option value="">Select project type</option>
              {projectTypeOptions.map((o) => (
                <option key={o.id} value={o.code}>{o.label}</option>
              ))}
            </select>
            {getError('project_type') && (
              <span id="project-type-error" className="input-group__error" role="alert">
                {getError('project_type')}
              </span>
            )}
          </div>
        </div>

        <div className="project-section__block">
          <h3 className="project-section__subheading">Scope</h3>
          <Input
            name="acreage"
            label="Acreage"
            type="number"
            min={0.01}
            max={10000}
            step={0.01}
            value={formValues.acreage}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('acreage')}
            required
          />
          <Input
            name="tree_count"
            label="Tree / shrub count"
            type="number"
            min={1}
            max={1000000}
            step={1}
            value={formValues.tree_count}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('tree_count')}
            required
          />
        </div>

        <div className="project-section__block">
          <h3 className="project-section__subheading">Timeline</h3>
          <DatePicker
            name="start_date"
            label="Expected start date"
            value={formValues.start_date}
            onChange={(e) => setFormValues((prev) => ({ ...prev, start_date: e.target.value }))}
            onBlur={handleBlur}
            error={getError('start_date')}
            required
          />
          <DatePicker
            name="completion_date"
            label="Expected completion date"
            value={formValues.completion_date}
            min={formValues.start_date || undefined}
            onChange={(e) => setFormValues((prev) => ({ ...prev, completion_date: e.target.value }))}
            onBlur={handleBlur}
            error={getError('completion_date')}
            required
          />
        </div>

        <div className="project-section__block">
          <h3 className="project-section__subheading">Description</h3>
          <div className="input-group">
            <label htmlFor="project-description" className="input-group__label">
              Project description <span className="input-group__required" aria-hidden="true">*</span>
            </label>
            <textarea
              id="project-description"
              name="description"
              value={formValues.description}
              onChange={handleChange}
              onBlur={handleBlur}
              maxLength={DESCRIPTION_MAX}
              rows={6}
              aria-required="true"
              aria-invalid={!!getError('description')}
              aria-describedby={getError('description') ? 'project-description-error' : 'project-description-counter'}
              className={`input-group__input ${getError('description') ? 'input-group__input--error' : ''}`}
              style={{ minHeight: '120px', resize: 'vertical' }}
            />
            <span id="project-description-counter" className="input-group__hint" aria-live="polite">
              {descriptionLen} / {DESCRIPTION_MAX} characters
            </span>
            {getError('description') && (
              <span id="project-description-error" className="input-group__error" role="alert">
                {getError('description')}
              </span>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
