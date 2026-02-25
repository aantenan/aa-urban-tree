/**
 * Complaint API: submit, list mine, get one, categories.
 * Admin: list all, update status, assign (uses same apiFetch with token).
 */
import { apiFetch, apiJson } from './api';

const V1 = '/api/v1/complaints';

export async function getCategories() {
  const res = await apiFetch(`${V1}/categories`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.message ?? 'Failed to load categories');
  return data?.data ?? data;
}

/** Submit complaint (optional auth via token). */
export async function submitComplaint({ subject, description, category = 'other', location_or_reference }) {
  const res = await apiFetch(`${V1}/submit`, {
    method: 'POST',
    body: JSON.stringify({ subject, description, category, location_or_reference: location_or_reference || null }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.message ?? 'Failed to submit complaint');
  return data?.data ?? data;
}

/** List current user's complaints (requires auth). */
export async function listMyComplaints() {
  const data = await apiJson(`${V1}`);
  return data?.data ?? data;
}

/** Get one complaint by id (own or admin). */
export async function getComplaint(id) {
  const data = await apiJson(`${V1}/${id}`);
  return data?.data ?? data;
}

/** Admin: list all complaints. */
export async function listAllComplaints({ status: statusFilter, category, limit = 100, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (statusFilter) params.set('status_filter', statusFilter);
  if (category) params.set('category', category);
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  const data = await apiJson(`${V1}/admin/all?${params.toString()}`);
  return data?.data ?? data;
}

/** Admin: update complaint status. */
export async function updateComplaintStatus(complaintId, { status, resolution_notes }) {
  const data = await apiJson(`${V1}/admin/${complaintId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, resolution_notes: resolution_notes || null }),
  });
  return data?.data ?? data;
}

/** Admin: assign complaint. */
export async function assignComplaint(complaintId, assigneeId) {
  const data = await apiJson(`${V1}/admin/${complaintId}/assign`, {
    method: 'PATCH',
    body: JSON.stringify({ assignee_id: assigneeId || null }),
  });
  return data?.data ?? data;
}
