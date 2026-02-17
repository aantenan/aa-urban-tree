/**
 * Public API client: program configuration for the listing page.
 * No auth; supports cache headers for optimal public access.
 */

const getBaseUrl = () => import.meta.env.VITE_API_BASE_URL || '';

/**
 * Fetch public program config from /api/config/program.
 * Returns program, grantCycle, eligibility, resources.
 * Falls back to /api/public/config for legacy shape.
 * @returns {Promise<object>}
 */
export async function getProgramConfig() {
  const base = getBaseUrl().replace(/\/$/, '');
  const url = `${base}/api/config/program`;
  const res = await fetch(url, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    credentials: 'omit',
  });
  if (!res.ok) {
    const fallback = await fetch(`${base}/api/public/config`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      credentials: 'omit',
    });
    if (fallback.ok) return fallback.json();
    throw new Error(res.statusText || 'Failed to load program config');
  }
  return res.json();
}
