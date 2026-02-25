/**
 * Form-filling agent API: guidance and extract from text.
 */
import { apiJson } from './api';

const V1 = '/api/v1/form-agent';

export async function getGuidance(section, currentData = null) {
  if (currentData) {
    const data = await apiJson(`${V1}/guidance`, {
      method: 'POST',
      body: JSON.stringify({ section, current_data: currentData }),
    });
    return data?.data ?? data;
  }
  const data = await apiJson(`${V1}/guidance?section=${encodeURIComponent(section)}`);
  return data?.data ?? data;
}

export async function extractFromText(section, text) {
  const data = await apiJson(`${V1}/extract`, {
    method: 'POST',
    body: JSON.stringify({ section, text }),
  });
  return data?.data ?? data;
}
