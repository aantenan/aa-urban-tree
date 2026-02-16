/**
 * Contact information validation (matches backend rules).
 * Returns object of field name -> error message (only fields with errors).
 */
import { required, email, phone } from './validation';

const FIELDS = [
  { key: 'organization_name', label: 'Organization name', validators: [required] },
  { key: 'address_line1', label: 'Address line 1', validators: [required] },
  { key: 'city', label: 'City', validators: [required] },
  { key: 'state_code', label: 'State', validators: [required] },
  { key: 'zip_code', label: 'ZIP code', validators: [required] },
  { key: 'county', label: 'County', validators: [required] },
  { key: 'primary_contact_name', label: 'Primary contact name', validators: [required] },
  { key: 'primary_contact_email', label: 'Primary contact email', validators: [required, email] },
  { key: 'primary_contact_phone', label: 'Primary contact phone', validators: [phone] },
  { key: 'alternate_contact_email', label: 'Alternate contact email', validators: [email] },
  { key: 'alternate_contact_phone', label: 'Alternate contact phone', validators: [phone] },
];

function runValidators(value, validators, fieldName) {
  for (const fn of validators) {
    const err = fn(value, fieldName);
    if (err) return err;
  }
  return null;
}

/**
 * @param {Record<string, string>} values - Form values (snake_case keys)
 * @returns {Record<string, string>} Field errors
 */
export function validateContactForm(values) {
  const errors = {};
  for (const { key, label, validators } of FIELDS) {
    const value = values[key];
    const err = runValidators(value, validators, label);
    if (err) errors[key] = err;
  }
  return errors;
}

/** Default empty contact form (snake_case, matches API). State default MD. */
export const CONTACT_INITIAL = {
  organization_name: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state_code: 'MD',
  zip_code: '',
  county: '',
  primary_contact_name: '',
  primary_contact_title: '',
  primary_contact_email: '',
  primary_contact_phone: '',
  alternate_contact_name: '',
  alternate_contact_title: '',
  alternate_contact_email: '',
  alternate_contact_phone: '',
};
