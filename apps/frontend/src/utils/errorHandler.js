/**
 * API and network error handling utilities.
 */

/**
 * @param {Error} err - Error from apiJson or fetch
 * @returns {string} User-friendly message
 */
export function getErrorMessage(err) {
  if (err?.data?.detail) {
    return typeof err.data.detail === 'string'
      ? err.data.detail
      : JSON.stringify(err.data.detail);
  }
  if (err?.message) return err.message;
  if (err?.status === 401) return 'Please sign in again.';
  if (err?.status === 403) return 'You do not have permission.';
  if (err?.status >= 500) return 'Server error. Please try again later.';
  return 'Something went wrong. Please try again.';
}
