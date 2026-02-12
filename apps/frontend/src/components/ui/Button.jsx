import React from 'react';

/**
 * Accessible button. Supports disabled, loading, type (button|submit|reset), and variant.
 * Use aria-busy when loading for screen readers.
 */
export function Button({
  children,
  disabled = false,
  loading = false,
  type = 'button',
  variant = 'primary',
  'aria-label': ariaLabel,
  className = '',
  ...props
}) {
  const isDisabled = disabled || loading;
  return (
    <button
      type={type}
      disabled={isDisabled}
      aria-busy={loading}
      aria-disabled={isDisabled}
      aria-label={ariaLabel}
      className={`btn btn--${variant} ${className}`.trim()}
      {...props}
    >
      {loading ? (
        <>
          <span className="btn__spinner" aria-hidden="true" />
          <span className="btn__text">{children}</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
