/**
 * Financial information validation (aligned with backend rules).
 * Total cost, grant, matching funds sum = total - grant, min 20% cost-match,
 * line items sum = total, valid categories.
 */

const MIN_MATCH_PERCENT = 20;
const FLOAT_TOLERANCE = 0.01;

function parseCurrency(value) {
  if (value == null || value === '') return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function roundCurrency(n) {
  return Math.round(n * 100) / 100;
}

/**
 * @param {Record<string, unknown>} values - Form values including total_project_cost, grant_amount_requested, matching_funds[], line_item_budget[]
 * @param {{ budgetCategoryCodes?: string[] }} options - Allowed budget category codes from API
 * @returns {Record<string, string>} Field errors (keys may be 'matching_funds', 'line_item_budget', or nested keys)
 */
export function validateFinancialForm(values, options = {}) {
  const { budgetCategoryCodes = [] } = options;
  const errors = {};

  const totalCost = parseCurrency(values.total_project_cost);
  if (totalCost == null) {
    if (values.total_project_cost !== '' && values.total_project_cost != null) {
      errors.total_project_cost = 'Enter a valid amount';
    } else {
      errors.total_project_cost = 'Total project cost is required';
    }
  } else if (totalCost < 0) {
    errors.total_project_cost = 'Total project cost must be zero or greater';
  }

  const grant = parseCurrency(values.grant_amount_requested);
  if (grant == null) {
    if (values.grant_amount_requested !== '' && values.grant_amount_requested != null) {
      errors.grant_amount_requested = 'Enter a valid amount';
    } else {
      errors.grant_amount_requested = 'Grant amount is required';
    }
  } else if (grant < 0) {
    errors.grant_amount_requested = 'Grant amount must be zero or greater';
  }

  const total = totalCost != null && totalCost >= 0 ? roundCurrency(totalCost) : null;
  const grantR = grant != null && grant >= 0 ? roundCurrency(grant) : null;

  if (total != null && grantR != null && grantR > total) {
    errors.grant_amount_requested = 'Grant amount cannot exceed total project cost';
  }

  const matchingList = Array.isArray(values.matching_funds) ? values.matching_funds : [];
  let matchingSum = 0;
  matchingList.forEach((item, i) => {
    if (!item || typeof item !== 'object') {
      errors[`matching_funds[${i}]`] = 'Invalid item';
      return;
    }
    const source = (item.source_name ?? '').trim();
    const amount = parseCurrency(item.amount);
    const type = (item.type ?? '').trim().toLowerCase();
    if (!source) errors[`matching_funds[${i}].source_name`] = 'Source name is required';
    if (amount == null || amount < 0) errors[`matching_funds[${i}].amount`] = 'Valid amount is required';
    if (type !== 'cash' && type !== 'in_kind') errors[`matching_funds[${i}].type`] = 'Type must be Cash or In-kind';
    if (amount != null && amount >= 0) matchingSum += amount;
  });
  matchingSum = roundCurrency(matchingSum);

  const expectedMatching = total != null && grantR != null ? roundCurrency(total - grantR) : null;
  if (expectedMatching != null && !errors.matching_funds && !Object.keys(errors).some((k) => k.startsWith('matching_funds'))) {
    if (Math.abs(matchingSum - expectedMatching) > FLOAT_TOLERANCE) {
      errors.matching_funds = `Matching funds total ($${matchingSum.toLocaleString('en-US', { minimumFractionDigits: 2 })}) must equal total cost minus grant ($${expectedMatching.toLocaleString('en-US', { minimumFractionDigits: 2 })})`;
    } else if (total > 0) {
      const matchPct = (matchingSum / total) * 100;
      if (matchPct < MIN_MATCH_PERCENT) {
        errors.matching_funds = `Cost-match percentage (${matchPct.toFixed(1)}%) must be at least ${MIN_MATCH_PERCENT}%`;
      }
    }
  }

  const lineList = Array.isArray(values.line_item_budget) ? values.line_item_budget : [];
  let lineSum = 0;
  lineList.forEach((item, i) => {
    if (!item || typeof item !== 'object') {
      errors[`line_item_budget[${i}]`] = 'Invalid item';
      return;
    }
    const category = (item.category ?? '').trim().toLowerCase();
    const amount = parseCurrency(item.amount);
    if (!category) errors[`line_item_budget[${i}].category`] = 'Category is required';
    else if (budgetCategoryCodes.length && !budgetCategoryCodes.includes(category)) {
      errors[`line_item_budget[${i}].category`] = 'Select a valid budget category';
    }
    if (amount == null || amount < 0) errors[`line_item_budget[${i}].amount`] = 'Valid amount is required';
    if (amount != null && amount >= 0) lineSum += amount;
  });
  lineSum = roundCurrency(lineSum);

  if (total != null && total >= 0 && lineList.length > 0 && !Object.keys(errors).some((k) => k.startsWith('line_item_budget'))) {
    if (Math.abs(lineSum - total) > FLOAT_TOLERANCE) {
      errors.line_item_budget = `Line items must sum to total project cost ($${total.toLocaleString('en-US', { minimumFractionDigits: 2 })})`;
    }
  }

  return errors;
}

/** Default empty financial form (matches API shape). */
export const FINANCIAL_INITIAL = {
  total_project_cost: '',
  grant_amount_requested: '',
  matching_funds: [],
  line_item_budget: [],
};

export const MIN_MATCH_PERCENT_REQUIRED = MIN_MATCH_PERCENT;
