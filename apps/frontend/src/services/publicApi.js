/**
 * Public API client: program configuration for the listing page.
 * No auth; supports cache headers for optimal public access.
 */

const getBaseUrl = () => import.meta.env.VITE_API_BASE_URL || '';

/**
 * Fetch public program config. Uses cache headers from backend.
 * @returns {Promise<{ title: string, description: string, resources: Array, ... }>}
 */
export async function getProgramConfig() {
  const base = getBaseUrl().replace(/\/$/, '');
  const url = `${base}/api/public/config`;
  const res = await fetch(url, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'omit',
  });
  if (!res.ok) throw new Error(res.statusText || 'Failed to load program config');
  return res.json();
}
