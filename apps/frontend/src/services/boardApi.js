/**
 * Forestry Board API: list applications, get details, approve, request revision.
 */
import { apiJson } from './api';

/**
 * List applications for the current board member's county.
 * @returns {Promise<{ applications: Array<{ applicationId, applicantName, organizationName, projectName, county, status, submittedForReviewDate }> }>}
 */
export async function listBoardApplications() {
  const res = await apiJson('/api/v1/board/board-members/me/applications');
  return res?.data ?? res;
}

/**
 * Get full application details for board review.
 * @param {string} applicationId
 * @returns {Promise<{ applicationId, applicantName, organizationName, projectName, projectDescription, county, status, sections, revisionHistory }>}
 */
export async function getBoardApplication(applicationId) {
  const res = await apiJson(`/api/v1/board/board-members/me/applications/${applicationId}`);
  return res?.data ?? res;
}

/**
 * Approve application with electronic signature.
 * @param {string} applicationId
 * @param {{ boardMemberName: string, boardMemberTitle?: string, approvalDate: string }} body
 */
export async function approveApplication(applicationId, body) {
  const res = await apiJson(`/api/v1/board/board-members/me/applications/${applicationId}/approve`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  return res;
}

/**
 * Request revisions with comments.
 * @param {string} applicationId
 * @param {{ comments: string }} body
 */
export async function requestRevision(applicationId, body) {
  const res = await apiJson(`/api/v1/board/board-members/me/applications/${applicationId}/request-revision`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  return res;
}

/**
 * List documents for an application (board member only).
 * @param {string} applicationId
 * @returns {Promise<{ documents: { sitePlan, sitePhotos, supportingDocuments } }>}
 */
export async function listBoardDocuments(applicationId) {
  const res = await apiJson(`/api/v1/board/board-members/me/applications/${applicationId}/documents`);
  return res?.data ?? res;
}

/**
 * Get document download URL (with auth). Use apiFetch with this path and Authorization header.
 * @param {string} applicationId
 * @param {string} documentId
 * @returns {string}
 */
export function getBoardDocumentDownloadPath(applicationId, documentId) {
  return `/api/v1/board/board-members/me/applications/${applicationId}/documents/${documentId}`;
}
