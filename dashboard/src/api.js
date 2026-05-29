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

export const downloadReport = async () => {
  const response = await axios.get(`${BASE}/report`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `verispect-compliance-report-${new Date().toISOString().slice(0,10)}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}