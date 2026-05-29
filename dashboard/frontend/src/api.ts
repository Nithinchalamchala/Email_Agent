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
};

export const fetchStats = async () =>
  (await axios.get(`${BASE}/api/stats`)).data;

export const fetchSyncStatus = async () =>
  (await axios.get(`${BASE}/api/sync-status`)).data;

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

// Calendar — all functions accept the MSAL token as X-Cal-Token header
const calHeaders = (token?: string) =>
  token ? { "X-Cal-Token": token } : {};

export const fetchCalendarEvents = async (days = 7, token?: string) =>
  (await axios.get(`${BASE}/api/calendar/events?days=${days}`, { headers: calHeaders(token) })).data;

export const fetchCalendars = async (token?: string) =>
  (await axios.get(`${BASE}/api/calendar/calendars`, { headers: calHeaders(token) })).data;

export const runCalendarPipeline = async (
  email: { sender: string; subject: string; body: string; timestamp: string },
  token?: string,
) => (await axios.post(`${BASE}/api/calendar/run`, email, { headers: calHeaders(token) })).data;
