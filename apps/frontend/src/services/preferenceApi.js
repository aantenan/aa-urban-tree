/**
 * Preference API: record interactions and get recommendations.
 */
import { apiJson } from './api';

const V1 = '/api/v1/preferences';

export async function recordInteraction({ interaction_type, target_id, metadata }) {
  const data = await apiJson(`${V1}/interaction`, {
    method: 'POST',
    body: JSON.stringify({
      interaction_type: interaction_type || 'page_view',
      target_id: target_id || null,
      metadata: metadata || null,
    }),
  });
  return data?.data ?? data;
}

export async function getRecommendations(limit = 5) {
  const data = await apiJson(`${V1}/recommendations?limit=${limit}`);
  return data?.data ?? data;
}
