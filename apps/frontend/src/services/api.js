/**
 * API client: base URL from env, token from localStorage, error handling.
 */

const getBaseUrl = () => import.meta.env.VITE_API_BASE_URL || '';

const getToken = () => localStorage.getItem('token');

/**
 * @param {string} path - Path relative to base URL (e.g. '/api/v1/health')
 * @param {RequestInit} [options]
 * @returns {Promise<Response>}
 */
export async function apiFetch(path, options = {}) {
  const base = getBaseUrl().replace(/\/$/, '');
  const url = path.startsWith('http') ? path : `${base}${path}`;
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(url, { ...options, headers });
  return res;
}

/**
 * Same as apiFetch but parse JSON and throw on non-2xx.
 * @returns {Promise<unknown>}
 */
export async function apiJson(path, options = {}) {
  const res = await apiFetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.detail || res.statusText || 'Request failed');
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export { getBaseUrl, getToken };
