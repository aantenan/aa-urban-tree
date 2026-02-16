/**
 * Project information validation (matches backend rules).
 * Returns object of field name -> error message.
 */
const ACREAGE_MIN = 0.01;
const ACREAGE_MAX = 10000;
const TREE_COUNT_MIN = 1;
const TREE_COUNT_MAX = 1_000_000;
const DESCRIPTION_MAX_LENGTH = 5000;

function required(value, fieldName = 'Field') {
  if (value == null || String(value).trim() === '') return `${fieldName} is required`;
  return null;
}

function parseNum(value) {
  if (value == null || value === '') return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function parseDate(value) {
  if (value == null || value === '') return null;
  const s = String(value).trim();
  if (!s) return null;
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? null : s;
}

/**
 * @param {Record<string, string|number>} values - Form values (snake_case)
 * @param {{ siteOwnershipCodes: string[], projectTypeCodes: string[] }} options - Allowed codes from API
 * @returns {Record<string, string>} Field errors
 */
export function validateProjectForm(values, options = {}) {
  const { siteOwnershipCodes = [], projectTypeCodes = [] } = options;
  const errors = {};

  const projectName = (values.project_name || '').trim();
  if (!projectName) errors.project_name = 'Project name is required';

  const siteAddr1 = (values.site_address_line1 || '').trim();
  if (!siteAddr1) errors.site_address_line1 = 'Site address is required';
  const siteCity = (values.site_city || '').trim();
  if (!siteCity) errors.site_city = 'Site city is required';
  const siteState = (values.site_state_code || '').trim();
  if (!siteState) errors.site_state_code = 'Site state is required';
  const siteZip = (values.site_zip_code || '').trim();
  if (!siteZip) errors.site_zip_code = 'Site ZIP code is required';

  const siteOwnership = (values.site_ownership || '').trim();
  if (!siteOwnership) errors.site_ownership = 'Site ownership is required';
  else if (siteOwnership && siteOwnershipCodes.length && !siteOwnershipCodes.includes(siteOwnership)) {
    errors.site_ownership = 'Select a valid site ownership option';
  }

  const projectType = (values.project_type || '').trim();
  if (!projectType) errors.project_type = 'Project type is required';
  else if (projectType && projectTypeCodes.length && !projectTypeCodes.includes(projectType)) {
    errors.project_type = 'Select a valid project type';
  }

  const acreage = parseNum(values.acreage);
  if (acreage == null) {
    if (values.acreage !== '' && values.acreage != null) errors.acreage = 'Enter a valid number';
    else errors.acreage = 'Acreage is required';
  } else if (acreage < ACREAGE_MIN || acreage > ACREAGE_MAX) {
    errors.acreage = `Acreage must be between ${ACREAGE_MIN} and ${ACREAGE_MAX}`;
  }

  const treeCount = parseNum(values.tree_count);
  if (treeCount == null) {
    if (values.tree_count !== '' && values.tree_count != null) errors.tree_count = 'Enter a valid whole number';
    else errors.tree_count = 'Tree count is required';
  } else {
    const intCount = Math.floor(treeCount);
    if (intCount !== treeCount) errors.tree_count = 'Tree count must be a whole number';
    else if (intCount < TREE_COUNT_MIN || intCount > TREE_COUNT_MAX) {
      errors.tree_count = `Tree count must be between ${TREE_COUNT_MIN} and ${TREE_COUNT_MAX}`;
    }
  }

  const startDate = parseDate(values.start_date);
  const completionDate = parseDate(values.completion_date);
  if (!startDate) errors.start_date = 'Start date is required';
  if (!completionDate) errors.completion_date = 'Completion date is required';
  if (startDate && completionDate && startDate > completionDate) {
    errors.completion_date = 'Completion date must be on or after start date';
  }

  const description = (values.description || '').trim();
  if (!description) errors.description = 'Project description is required';
  else if (description.length > DESCRIPTION_MAX_LENGTH) {
    errors.description = `Description must be ${DESCRIPTION_MAX_LENGTH} characters or fewer`;
  }

  return errors;
}

export const DESCRIPTION_MAX = DESCRIPTION_MAX_LENGTH;

/** Default empty project form (snake_case, matches API). */
export const PROJECT_INITIAL = {
  project_name: '',
  site_address_line1: '',
  site_address_line2: '',
  site_city: '',
  site_state_code: '',
  site_zip_code: '',
  site_ownership: '',
  project_type: '',
  acreage: '',
  tree_count: '',
  start_date: '',
  completion_date: '',
  description: '',
};
