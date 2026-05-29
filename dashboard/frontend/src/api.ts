import axios from 'axios';

// TODO: move to env var (REACT_APP_API_BASE) before deploying
const BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8001';

export const fetchBatch = async () =>
  (await axios.get(`${BASE}/api/batch`)).data.results;

export const fetchEmail = async (id: string) =>
  (await axios.get(`${BASE}/api/email/${id}`)).data;

// Calendar
export const fetchCalendarEvents = async (days = 7) =>
  (await axios.get(`${BASE}/api/calendar/events?days=${days}`)).data;

export const fetchCalendars = async () =>
  (await axios.get(`${BASE}/api/calendar/calendars`)).data;

export const runCalendarPipeline = async (email: {
  sender: string;
  subject: string;
  body: string;
  timestamp: string;
}) => (await axios.post(`${BASE}/api/calendar/run`, email)).data;
