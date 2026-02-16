import React, { useCallback, useEffect, useState } from 'react';
import { apiJson } from '../services/api';
import { getErrorMessage } from '../utils/errorHandler';
import {
  validateFinancialForm,
  FINANCIAL_INITIAL,
  MIN_MATCH_PERCENT_REQUIRED,
} from '../utils/financialValidation';
import { useAutoSave } from '../hooks/useAutoSave';
import { Button, Input } from './ui';
import { LoadingSpinner } from './LoadingSpinner';

const AUTO_SAVE_DELAY_MS = 1500;

function parseNum(v) {
  if (v == null || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function roundCurrency(n) {
  return Math.round(n * 100) / 100;
}

/**
 * Financial information section: total cost, grant, matching funds (add/remove),
 * line item budget (add/remove), real-time cost-match %, section completion, auto-save.
 * GET/PUT /api/v1/applications/{id}/financial-information; budget categories from /api/v1/budget-categories.
 */
export function FinancialInformationSection({ applicationId }) {
  const [formValues, setFormValues] = useState(FINANCIAL_INITIAL);
  const [budgetCategories, setBudgetCategories] = useState([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [financialLoading, setFinancialLoading] = useState(!!applicationId);
  const [loadError, setLoadError] = useState('');
  const [saveStatus, setSaveStatus] = useState('idle');
  const [apiError, setApiError] = useState('');
  const [sectionComplete, setSectionComplete] = useState(false);
  const [backendErrors, setBackendErrors] = useState(null);
  const [touched, setTouched] = useState({});
  const [serverCostMatchPercent, setServerCostMatchPercent] = useState(null);

  const budgetCategoryCodes = budgetCategories.map((c) => c.code);

  useEffect(() => {
    let cancelled = false;
    apiJson('/api/v1/budget-categories')
      .then((res) => {
        if (cancelled) return;
        const list = res?.data ?? res;
        setBudgetCategories(Array.isArray(list) ? list : []);
      })
      .catch(() => {
        if (!cancelled) setBudgetCategories([]);
      })
      .finally(() => {
        if (!cancelled) setCategoriesLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const loadFinancial = useCallback(() => {
    if (!applicationId) return;
    setFinancialLoading(true);
    setLoadError('');
    apiJson(`/api/v1/applications/${applicationId}/financial-information`)
      .then((res) => {
        const data = res?.data ?? res;
        const fi = data?.financial_information;
        setSectionComplete(!!data?.section_complete);
        setServerCostMatchPercent(fi?.cost_match_percentage ?? null);
        setBackendErrors(null);
        if (!fi) {
          setFormValues(FINANCIAL_INITIAL);
          return;
        }
        setFormValues({
          total_project_cost: fi.total_project_cost != null ? String(fi.total_project_cost) : '',
          grant_amount_requested: fi.grant_amount_requested != null ? String(fi.grant_amount_requested) : '',
          matching_funds: Array.isArray(fi.matching_funds)
            ? fi.matching_funds.map((m) => ({
                source_name: m.source_name ?? '',
                amount: m.amount != null ? String(m.amount) : '',
                type: m.type === 'in_kind' ? 'in_kind' : 'cash',
              }))
            : [],
          line_item_budget: Array.isArray(fi.line_item_budget)
            ? fi.line_item_budget.map((l) => ({
                category: l.category ?? '',
                description: l.description ?? '',
                amount: l.amount != null ? String(l.amount) : '',
              }))
            : [],
        });
      })
      .catch((err) => {
        setLoadError(getErrorMessage(err));
      })
      .finally(() => {
        setFinancialLoading(false);
      });
  }, [applicationId]);

  useEffect(() => {
    if (!applicationId) {
      setFormValues(FINANCIAL_INITIAL);
      setSectionComplete(false);
      setFinancialLoading(false);
      setServerCostMatchPercent(null);
      return;
    }
    loadFinancial();
  }, [applicationId, loadFinancial]);

  const buildPayload = useCallback((vals) => {
    const total = parseNum(vals.total_project_cost);
    const grant = parseNum(vals.grant_amount_requested);
    const matching_funds = (vals.matching_funds || []).map((m) => ({
      source_name: (m.source_name || '').trim(),
      amount: roundCurrency(parseNum(m.amount) ?? 0),
      type: (m.type || 'cash').trim().toLowerCase() === 'in_kind' ? 'in_kind' : 'cash',
    }));
    const line_item_budget = (vals.line_item_budget || []).map((l) => ({
      category: (l.category || '').trim().toLowerCase(),
      description: (l.description || '').trim(),
      amount: roundCurrency(parseNum(l.amount) ?? 0),
    }));
    return {
      total_project_cost: total != null ? roundCurrency(total) : null,
      grant_amount_requested: grant != null ? roundCurrency(grant) : null,
      matching_funds,
      line_item_budget,
    };
  }, []);

  const saveFinancial = useCallback(async (payload) => {
    if (!applicationId) return;
    setSaveStatus('saving');
    setApiError('');
    const body = buildPayload(payload);
    try {
      const res = await apiJson(`/api/v1/applications/${applicationId}/financial-information`, {
        method: 'PUT',
        body: JSON.stringify(body),
      });
      const data = res?.data ?? res;
      setSectionComplete(!!data?.section_complete);
      setBackendErrors(data?.errors ?? null);
      const fi = data?.financial_information;
      setServerCostMatchPercent(fi?.cost_match_percentage ?? null);
      setSaveStatus('saved');
    } catch (err) {
      setApiError(getErrorMessage(err));
      setSaveStatus('error');
    }
  }, [applicationId, buildPayload]);

  useAutoSave(formValues, saveFinancial, {
    delay: AUTO_SAVE_DELAY_MS,
    enabled: !!applicationId && !financialLoading,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleBlur = (e) => {
    setTouched((prev) => ({ ...prev, [e.target.name]: true }));
  };

  const setMatchingFund = (index, field, value) => {
    setFormValues((prev) => {
      const list = [...(prev.matching_funds || [])];
      list[index] = { ...list[index], [field]: value };
      return { ...prev, matching_funds: list };
    });
  };

  const addMatchingFund = () => {
    setFormValues((prev) => ({
      ...prev,
      matching_funds: [...(prev.matching_funds || []), { source_name: '', amount: '', type: 'cash' }],
    }));
  };

  const removeMatchingFund = (index) => {
    setFormValues((prev) => {
      const list = [...(prev.matching_funds || [])];
      list.splice(index, 1);
      return { ...prev, matching_funds: list };
    });
  };

  const setLineItem = (index, field, value) => {
    setFormValues((prev) => {
      const list = [...(prev.line_item_budget || [])];
      list[index] = { ...list[index], [field]: value };
      return { ...prev, line_item_budget: list };
    });
  };

  const addLineItem = () => {
    setFormValues((prev) => ({
      ...prev,
      line_item_budget: [...(prev.line_item_budget || []), { category: '', description: '', amount: '' }],
    }));
  };

  const removeLineItem = (index) => {
    setFormValues((prev) => {
      const list = [...(prev.line_item_budget || [])];
      list.splice(index, 1);
      return { ...prev, line_item_budget: list };
    });
  };

  const clientErrors = validateFinancialForm(formValues, { budgetCategoryCodes });
  const getError = (key) => backendErrors?.[key] ?? (touched[key] ? clientErrors[key] : null);
  const getMatchingError = (index, field) => {
    const key = `matching_funds[${index}].${field}`;
    return backendErrors?.[key] ?? clientErrors[key] ?? null;
  };
  const getLineError = (index, field) => {
    const key = `line_item_budget[${index}].${field}`;
    return backendErrors?.[key] ?? clientErrors[key] ?? null;
  };

  const totalNum = parseNum(formValues.total_project_cost);
  const grantNum = parseNum(formValues.grant_amount_requested);
  const matchingList = formValues.matching_funds || [];
  const matchingSum = roundCurrency(
    matchingList.reduce((acc, m) => acc + (parseNum(m.amount) ?? 0), 0)
  );
  const lineList = formValues.line_item_budget || [];
  const lineSum = roundCurrency(lineList.reduce((acc, l) => acc + (parseNum(l.amount) ?? 0), 0));

  const liveCostMatchPercent =
    totalNum != null && totalNum > 0 && matchingSum >= 0
      ? roundCurrency((matchingSum / totalNum) * 100)
      : null;
  const costMatchPercent = serverCostMatchPercent ?? liveCostMatchPercent;
  const costMatchCompliant =
    costMatchPercent != null && costMatchPercent >= MIN_MATCH_PERCENT_REQUIRED;

  if (financialLoading && applicationId) {
    return (
      <section className="form-section financial-section" aria-labelledby="financial-heading">
        <h2 id="financial-heading">Financial Information</h2>
        <LoadingSpinner />
      </section>
    );
  }

  return (
    <section
      className="form-section financial-section"
      aria-labelledby="financial-heading"
      aria-describedby="financial-status"
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <h2 id="financial-heading" style={{ margin: 0 }}>
          Financial Information
        </h2>
        <span
          id="financial-status"
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
          <Button type="button" variant="secondary" onClick={loadFinancial} style={{ marginLeft: '0.5rem' }}>
            Retry
          </Button>
        </p>
      )}
      {apiError && (
        <p role="alert" className="form-section__error">
          {apiError}
        </p>
      )}

      <div className="financial-section__grid">
        <div className="financial-section__block">
          <h3 className="financial-section__subheading">Project cost and grant</h3>
          <Input
            name="total_project_cost"
            label="Total project cost ($)"
            type="number"
            min={0}
            step={0.01}
            value={formValues.total_project_cost}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('total_project_cost')}
            required
            aria-required="true"
          />
          <Input
            name="grant_amount_requested"
            label="Grant amount requested ($)"
            type="number"
            min={0}
            step={0.01}
            value={formValues.grant_amount_requested}
            onChange={handleChange}
            onBlur={handleBlur}
            error={getError('grant_amount_requested')}
            required
            aria-required="true"
          />
          {totalNum != null && grantNum != null && totalNum >= 0 && grantNum >= 0 && (
            <p className="financial-section__hint" aria-live="polite">
              Matching funds required: ${(roundCurrency(totalNum - grantNum)).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          )}
        </div>

        <div className="financial-section__block">
          <h3 className="financial-section__subheading">Cost-match percentage</h3>
          <div
            className="financial-section__cost-match"
            role="status"
            aria-live="polite"
            style={{
              padding: '0.5rem 0.75rem',
              borderRadius: 6,
              fontSize: '1.125rem',
              fontWeight: 600,
              background: costMatchPercent == null ? '#f5f5f5' : costMatchCompliant ? '#e8f5e9' : '#ffebee',
              color: costMatchPercent == null ? '#333' : costMatchCompliant ? '#1b5e20' : '#c62828',
            }}
          >
            {costMatchPercent != null
              ? `Cost-match: ${costMatchPercent.toFixed(1)}%${costMatchCompliant ? ' ✓' : ` (minimum ${MIN_MATCH_PERCENT_REQUIRED}%)`}`
              : 'Enter total cost and matching funds to see cost-match %'}
          </div>
        </div>

        <div className="financial-section__block financial-section__block--wide">
          <h3 className="financial-section__subheading">Matching funds</h3>
          {backendErrors?.matching_funds && (
            <p role="alert" className="input-group__error" style={{ marginBottom: '0.5rem' }}>
              {backendErrors.matching_funds}
            </p>
          )}
          {matchingList.map((row, i) => (
            <div key={i} className="financial-section__row" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <input
                type="text"
                aria-label={`Matching source ${i + 1} name`}
                placeholder="Source name"
                value={row.source_name}
                onChange={(e) => setMatchingFund(i, 'source_name', e.target.value)}
                className="input-group__input"
                style={{ flex: '1 1 120px', minWidth: 100 }}
              />
              <input
                type="number"
                min={0}
                step={0.01}
                aria-label={`Matching source ${i + 1} amount`}
                placeholder="Amount"
                value={row.amount}
                onChange={(e) => setMatchingFund(i, 'amount', e.target.value)}
                className="input-group__input"
                style={{ width: '100px' }}
              />
              <select
                aria-label={`Matching source ${i + 1} type`}
                value={row.type || 'cash'}
                onChange={(e) => setMatchingFund(i, 'type', e.target.value)}
                className="input-group__input"
                style={{ width: '110px' }}
              >
                <option value="cash">Cash</option>
                <option value="in_kind">In-kind</option>
              </select>
              <Button type="button" variant="secondary" onClick={() => removeMatchingFund(i)} aria-label={`Remove matching source ${i + 1}`}>
                Remove
              </Button>
              {(getMatchingError(i, 'source_name') || getMatchingError(i, 'amount') || getMatchingError(i, 'type')) && (
                <span className="input-group__error" role="alert" style={{ width: '100%' }}>
                  {getMatchingError(i, 'source_name') || getMatchingError(i, 'amount') || getMatchingError(i, 'type')}
                </span>
              )}
            </div>
          ))}
          <Button type="button" variant="secondary" onClick={addMatchingFund}>
            Add matching source
          </Button>
        </div>

        <div className="financial-section__block financial-section__block--wide">
          <h3 className="financial-section__subheading">Line item budget</h3>
          {backendErrors?.line_item_budget && (
            <p role="alert" className="input-group__error" style={{ marginBottom: '0.5rem' }}>
              {backendErrors.line_item_budget}
            </p>
          )}
          {lineList.map((row, i) => (
            <div key={i} className="financial-section__row" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <select
                aria-label={`Line item ${i + 1} category`}
                value={row.category}
                onChange={(e) => setLineItem(i, 'category', e.target.value)}
                className="input-group__input"
                disabled={categoriesLoading}
                style={{ minWidth: 120 }}
              >
                <option value="">Category</option>
                {budgetCategories.map((c) => (
                  <option key={c.id} value={c.code}>
                    {c.label}
                  </option>
                ))}
              </select>
              <input
                type="text"
                aria-label={`Line item ${i + 1} description`}
                placeholder="Description"
                value={row.description}
                onChange={(e) => setLineItem(i, 'description', e.target.value)}
                className="input-group__input"
                style={{ flex: '1 1 140px', minWidth: 100 }}
              />
              <input
                type="number"
                min={0}
                step={0.01}
                aria-label={`Line item ${i + 1} amount`}
                placeholder="Amount"
                value={row.amount}
                onChange={(e) => setLineItem(i, 'amount', e.target.value)}
                className="input-group__input"
                style={{ width: 100 }}
              />
              <Button type="button" variant="secondary" onClick={() => removeLineItem(i)} aria-label={`Remove line item ${i + 1}`}>
                Remove
              </Button>
              {(getLineError(i, 'category') || getLineError(i, 'amount')) && (
                <span className="input-group__error" role="alert" style={{ width: '100%' }}>
                  {getLineError(i, 'category') || getLineError(i, 'amount')}
                </span>
              )}
            </div>
          ))}
          <Button type="button" variant="secondary" onClick={addLineItem}>
            Add line item
          </Button>
          {lineList.length > 0 && totalNum != null && (
            <p className="financial-section__hint" aria-live="polite" style={{ marginTop: '0.5rem' }}>
              Line items total: ${lineSum.toLocaleString('en-US', { minimumFractionDigits: 2 })} {totalNum > 0 && Math.abs(lineSum - totalNum) > 0.01 && `(target: $${totalNum.toLocaleString('en-US', { minimumFractionDigits: 2 })})`}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
