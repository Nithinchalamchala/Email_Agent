import axios from 'axios';

const BASE = 'http://localhost:8000';

interface BatchParams {
  page?: number;
  limit?: number;
  filter?: string;
  search?: string;
  priority?: string;
  safety?: string;
  action?: string;
}

export const fetchBatch = async (params: BatchParams = {}) => {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, String(v));
  });
  return (await axios.get(`${BASE}/api/batch?${qs}`)).data;
  // Returns: { results, total, page, limit, has_more }
};

export const fetchStats = async () =>
  (await axios.get(`${BASE}/api/stats`)).data;
  // Returns: { total, unread, needs_review, high_priority }

export const fetchSyncStatus = async () =>
  (await axios.get(`${BASE}/api/sync-status`)).data;
  // Returns: { last_sync, ai_status, connected_account, user_email }

export const fetchEmail = async (id: string) =>
  (await axios.get(`${BASE}/api/email/${id}`)).data;

export const markEmailRead = async (id: string) =>
  (await axios.patch(`${BASE}/api/email/${id}/mark-read`)).data;

export const triggerEmailFetch = async (graphToken: string) =>
  (await axios.post(
    `${BASE}/api/fetch-emails`,
    {},
    { headers: { "X-MS-GRAPH-TOKEN": graphToken } },
  )).data;
  // Returns: { success, processed, skipped, emails }
