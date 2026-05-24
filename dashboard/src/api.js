import axios from 'axios'

// Use relative path in production (same origin), absolute in local dev
const BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000/api'
  : '/api'

export const getMetrics = () => axios.get(`${BASE}/metrics`).then(r => r.data)
export const getLogs = () => axios.get(`${BASE}/logs`).then(r => r.data)
export const getDriftEvents = () => axios.get(`${BASE}/drift-events`).then(r => r.data)
export const getDriftTimeline = () => axios.get(`${BASE}/drift-timeline`).then(r => r.data)
export const getComplianceSummary = () => axios.get(`${BASE}/compliance-summary`).then(r => r.data)