import React from 'react';
import { passwordStrength } from '../utils/validation';

/**
 * Real-time password strength indicator (0–4 bars) and optional message.
 */
export function PasswordStrengthIndicator({ password = '' }) {
  const { strength, message, valid } = passwordStrength(password);
  if (!password) return null;
  return (
    <div className="password-strength" aria-live="polite">
      <div className="password-strength__bars" role="presentation">
        {[1, 2, 3, 4].map((i) => (
          <span
            key={i}
            className={`password-strength__bar ${i <= strength ? 'password-strength__bar--on' : ''}`}
          />
        ))}
      </div>
      {message && (
        <span className={`password-strength__message ${valid ? 'password-strength__message--ok' : ''}`}>
          {message}
        </span>
      )}
    </div>
  );
}
