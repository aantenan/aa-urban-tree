import React from 'react';

/**
 * Form wrapper with onSubmit and optional loading/disabled submit state.
 * Use with useForm for validation and submit state.
 */
export function Form({
  children,
  onSubmit,
  loading = false,
  className = '',
  'aria-label': ariaLabel,
  ...props
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.(e);
  };
  return (
    <form
      onSubmit={handleSubmit}
      className={`form ${className}`.trim()}
      aria-label={ariaLabel}
      noValidate
      {...props}
    >
      {children}
    </form>
  );
}
