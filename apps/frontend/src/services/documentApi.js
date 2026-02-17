/**
 * Document management API: upload, list, status, download, delete.
 */
import { apiFetch, apiJson, getBaseUrl, getToken } from './api';

const base = () => getBaseUrl().replace(/\/$/, '');
const authHeaders = () => {
  const token = getToken();
  const h = {};
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
};

/**
 * Upload a document. Uses multipart/form-data.
 * @param {string} applicationId
 * @param {File} file
 * @param {string} category - site_plan | site_photos | supporting_documents
 * @param {(percent: number) => void} [onProgress]
 * @returns {Promise<{ success: boolean, data?: object }>}
 */
export async function uploadDocument(applicationId, file, category, onProgress) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);

  const url = `${base()}/api/v1/applications/${applicationId}/documents`;
  const xhr = new XMLHttpRequest();
  xhr.open('POST', url);
  xhr.setRequestHeader('Authorization', `Bearer ${getToken()}`);
  xhr.responseType = 'json';

  return new Promise((resolve, reject) => {
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };
    xhr.onload = () => {
      try {
        const data = xhr.response && typeof xhr.response === 'object' ? xhr.response : JSON.parse(xhr.responseText || '{}');
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(data);
        } else {
          const err = new Error(data?.message ?? data?.detail ?? 'Upload failed');
          err.status = xhr.status;
          err.data = data;
          reject(err);
        }
      } catch {
        reject(new Error('Invalid response'));
      }
    };
    xhr.onerror = () => reject(new Error('Network error'));
    xhr.send(formData);
  });
}

/**
 * List documents grouped by category.
 * @param {string} applicationId
 * @returns {Promise<{ documents: { sitePlan: [], sitePhotos: [], supportingDocuments: [] } }>}
 */
export async function listDocuments(applicationId) {
  const res = await apiJson(`/api/v1/applications/${applicationId}/documents`);
  return res?.data ?? res;
}

/**
 * Get document completion status.
 * @param {string} applicationId
 * @returns {Promise<{ sitePlanUploaded: boolean, sitePhotosUploaded: boolean, allRequiredDocumentsUploaded: boolean }>}
 */
export async function getDocumentStatus(applicationId) {
  const res = await apiJson(`/api/v1/applications/${applicationId}/documents/status`);
  return res?.data ?? res;
}

/**
 * Delete a document.
 * @param {string} applicationId
 * @param {string} documentId
 */
export async function deleteDocument(applicationId, documentId) {
  await apiJson(`/api/v1/applications/${applicationId}/documents/${documentId}`, { method: 'DELETE' });
}

/**
 * Fetch thumbnail and return blob URL. Caller should revoke when done.
 * @param {string} applicationId
 * @param {string} documentId
 * @returns {Promise<string|null>} Blob URL or null
 */
export async function getThumbnailUrl(applicationId, documentId) {
  const res = await apiFetch(`/api/v1/applications/${applicationId}/documents/${documentId}/thumbnail`, {
    headers: authHeaders(),
  });
  if (!res.ok) return null;
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

/**
 * Download a document. Returns blob URL; caller should revoke when done.
 * @param {string} applicationId
 * @param {string} documentId
 * @param {string} [fileName] - suggested filename for download
 * @returns {Promise<{ url: string, fileName: string }>}
 */
export async function downloadDocument(applicationId, documentId, fileName) {
  const res = await apiFetch(`/api/v1/applications/${applicationId}/documents/${documentId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const err = new Error(data?.message ?? data?.detail ?? 'Download failed');
    err.status = res.status;
    err.data = data;
    throw err;
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const disposition = res.headers.get('Content-Disposition');
  let name = fileName;
  if (!name && disposition) {
    const m = disposition.match(/filename="?([^";\n]+)"?/);
    if (m) name = m[1].trim();
  }
  return { url, fileName: name || 'document' };
}
