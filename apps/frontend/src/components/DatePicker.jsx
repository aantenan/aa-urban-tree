import React from 'react';

/**
 * Date input with consistent formatting. Uses native input type="date" for accessibility.
 * Min/max in YYYY-MM-DD; value/onChange for controlled use.
 */
export function DatePicker({
  id,
  name,
  label,
  value,
  onChange,
  min,
  max,
  error,
  hint,
  required = false,
  disabled = false,
  className = '',
  ...props
}) {
  const inputId = id || `date-${name}`;
  return (
    <div className={`input-group date-picker ${className}`.trim()}>
      {label && (
        <label htmlFor={inputId} className="input-group__label">
          {label}
          {required && <span className="input-group__required" aria-hidden="true"> *</span>}
        </label>
      )}
      <input
        id={inputId}
        name={name}
        type="date"
        value={value ?? ''}
        onChange={onChange}
        min={min}
        max={max}
        required={required}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
        className={`input-group__input ${error ? 'input-group__input--error' : ''}`}
        {...props}
      />
      {hint && !error && <span id={`${inputId}-hint`} className="input-group__hint">{hint}</span>}
      {error && (
        <span id={`${inputId}-error`} className="input-group__error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
