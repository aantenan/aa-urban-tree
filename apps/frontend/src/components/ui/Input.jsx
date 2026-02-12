import React from 'react';

/**
 * Accessible text input with label, error, and optional hint.
 * Use id/labelId for aria-describedby when error or hint present.
 */
export function Input({
  id,
  name,
  label,
  type = 'text',
  error,
  hint,
  required = false,
  disabled = false,
  'aria-describedby': ariaDescribedby,
  className = '',
  ...props
}) {
  const describedBy = [error && `${id || name}-error`, hint && `${id || name}-hint`].filter(Boolean).join(' ') || undefined;
  const inputId = id || `input-${name}`;
  return (
    <div className={`input-group ${className}`.trim()}>
      {label && (
        <label htmlFor={inputId} className="input-group__label">
          {label}
          {required && <span className="input-group__required" aria-hidden="true"> *</span>}
        </label>
      )}
      <input
        id={inputId}
        name={name}
        type={type}
        required={required}
        disabled={disabled}
        aria-invalid={!!error}
        aria-required={required}
        aria-describedby={describedBy || ariaDescribedby}
        className={`input-group__input ${error ? 'input-group__input--error' : ''}`}
        {...props}
      />
      {hint && !error && (
        <span id={`${id || name}-hint`} className="input-group__hint">
          {hint}
        </span>
      )}
      {error && (
        <span id={`${id || name}-error`} className="input-group__error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
