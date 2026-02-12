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

/**
 * Password complexity: at least 8 chars, uppercase, lowercase, number, special.
 * Returns { valid: boolean, message?: string, strength: 0-4 }.
 */
export function passwordStrength(value) {
  if (value == null || value === '') {
    return { valid: false, strength: 0, message: 'Password is required' };
  }
  const s = String(value);
  let strength = 0;
  if (s.length >= 8) strength++;
  if (/[A-Z]/.test(s)) strength++;
  if (/[a-z]/.test(s)) strength++;
  if (/\d/.test(s)) strength++;
  if (/[^A-Za-z0-9]/.test(s)) strength++;
  const valid = s.length >= 8 && /[A-Z]/.test(s) && /[a-z]/.test(s) && /\d/.test(s);
  let message = null;
  if (!valid) {
    if (s.length < 8) message = 'At least 8 characters required';
    else if (!/[A-Z]/.test(s)) message = 'Add an uppercase letter';
    else if (!/[a-z]/.test(s)) message = 'Add a lowercase letter';
    else if (!/\d/.test(s)) message = 'Add a number';
    else message = 'Password does not meet requirements';
  }
  return { valid, strength: Math.min(4, strength), message };
}
