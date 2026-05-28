import axios from 'axios';

export const fetchBatch = async () =>
  (await axios.get('http://localhost:8000/api/batch')).data.results;

export const fetchEmail = async (id: string) =>
  (await axios.get(`http://localhost:8000/api/email/${id}`)).data;
