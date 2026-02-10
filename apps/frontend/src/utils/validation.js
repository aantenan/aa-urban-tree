/**
 * Simple form validation helpers.
 */

export function required(value, fieldName = 'Field') {
  if (value == null || String(value).trim() === '') {
    return `${fieldName} is required`;
  }
  return null;
}

export function minLength(value, min, fieldName = 'Field') {
  if (value != null && String(value).length < min) {
    return `${fieldName} must be at least ${min} characters`;
  }
  return null;
}

export function email(value) {
  if (value == null || value === '') return null;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(value) ? null : 'Enter a valid email address';
}

/**
 * Run validators in order; return first error or null.
 * @param {unknown} value
 * @param {Array<(v: unknown) => string | null>} validators
 * @returns {string | null}
 */
export function validate(value, validators) {
  for (const fn of validators) {
    const err = fn(value);
    if (err) return err;
  }
  return null;
}
